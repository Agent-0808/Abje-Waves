"""视频渲染器"""

import os
import time

import cv2
import imageio
import numpy as np

from .config import Config, NoteDuration
from .logger import format_duration, logger, setup_logger
from .wave import Wave


class Renderer:
    """视频渲染器"""
    
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.waves: list[Wave] = []
        setup_logger()
    
    def add_wave(self, wave: Wave) -> None:
        """添加单个波纹"""
        wave._config = self.config
        wave.__post_init__()
        self.waves.append(wave)
    
    def add_waves(self, waves: list[Wave]) -> None:
        """添加多个波纹"""
        for wave in waves:
            self.add_wave(wave)
    
    def add_wave_params(
        self,
        params_list: list[dict],
        interval: NoteDuration | None = None,
        start_time: float = 0.0,
    ) -> None:
        """添加波纹参数列表，自动计算时间间隔"""
        if interval is None:
            interval = self.config.content.interval
        interval_seconds = self.config.seconds_for_duration(interval)
        for i, params in enumerate(params_list):
            wave = Wave(
                time_start=start_time + i * interval_seconds,
                _config=self.config,
                **params
            )
            wave.__post_init__()
            self.waves.append(wave)
    
    def calculate_total_frames(self) -> int:
        """根据所有波纹计算总帧数"""
        if not self.waves:
            return 0
        last_time = max(w.time_start for w in self.waves)
        total_time = last_time + self.config.wave_duration
        return int(total_time * self.config.fps) + 1
    
    def _get_writer(self, output_path: str, fps: int):
        """根据格式获取对应的 writer"""
        fmt = self.config.render.format
        
        if fmt == "mov":
            return imageio.get_writer(
                output_path,
                fps=fps,
                format='FFMPEG',
                codec='prores_ks',
                pixelformat='yuva444p10le',
                macro_block_size=None,
                output_params=['-profile:v', '4444']
            )
        elif fmt == "mp4":
            return imageio.get_writer(
                output_path,
                fps=fps,
                format='FFMPEG',
                codec='libx264',
                pixelformat='yuv420p',
                macro_block_size=None,
                output_params=['-crf', '18']
            )
        else:
            raise ValueError(f"不支持的格式: {fmt}")
    
    def render(self, total_frames: int | None = None) -> None:
        """渲染视频"""
        if total_frames is None:
            total_frames = self.calculate_total_frames()
        
        width, height = self.config.width, self.config.height
        max_radius = self.config.get_max_radius()
        fps = self.config.fps
        output_path = self.config.get_output_path()
        
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        writer = self._get_writer(output_path, fps)
        
        logger.info(f"Start rendering: {output_path}")
        logger.info(f"Resolution: {width}x{height}, FPS: {fps}, Frames: {total_frames}")
        
        start_time = time.perf_counter()
        
        # 在循环外预分配内存
        canvas_rgba = np.zeros((height, width, 4), dtype=np.float32)
        halo_layer = np.zeros((height, width, 4), dtype=np.float32)
        core_layer = np.zeros((height, width, 4), dtype=np.float32)
        temp_layer = np.zeros((height, width, 4), dtype=np.float32)
        
        for frame_idx in range(total_frames):
            current_time = frame_idx / fps
            halo_layer.fill(0)
            core_layer.fill(0)
            
            for wave in self.waves:
                if wave.time_start > current_time:
                    continue
                
                if not wave.is_alive_at_time(current_time, max_radius):
                    continue
                
                radius = wave.get_radius_at_time(current_time)
                
                base_thickness = wave.thickness
                base_color = wave.color
                brightness = wave.brightness
                
                # 绘制光晕层 (较粗，使用指定颜色)
                temp_layer.fill(0)
                halo_color = (
                    base_color[0] * brightness,
                    base_color[1] * brightness,
                    base_color[2] * brightness,
                    255 * brightness
                )
                cv2.circle(
                    temp_layer,
                    (wave.x, wave.y),
                    int(radius),
                    color=halo_color,
                    thickness=int(base_thickness * 3.0),
                    lineType=cv2.LINE_AA 
                )
                halo_layer += temp_layer
                
                # 绘制核心层 (较细，纯白色)
                temp_layer.fill(0)
                core_color = (255, 255, 255, 255 * brightness)
                cv2.circle(
                    temp_layer,
                    (wave.x, wave.y),
                    int(radius),
                    color=core_color,
                    thickness=max(1, int(base_thickness * 0.6)),
                    lineType=cv2.LINE_AA 
                )
                core_layer += temp_layer
            
            # 对光晕层进行高斯模糊，形成平滑的渐变过渡
            if np.any(halo_layer):
                # 使用较大的 sigmaX 自动计算合适的核大小，实现大范围的柔和光晕
                cv2.GaussianBlur(halo_layer, (0, 0), sigmaX=15.0, dst=halo_layer)
            
            # 合并光晕层和核心层
            canvas_rgba = halo_layer + core_layer
            
            # 对最终画面进行轻微模糊，使核心边缘不那么生硬
            if np.any(canvas_rgba):
                cv2.GaussianBlur(canvas_rgba, (3, 3), 0, dst=canvas_rgba)

            frame_out = np.clip(canvas_rgba, 0, 255).astype(np.uint8)
            writer.append_data(frame_out)
            
            if frame_idx % 20 == 0:
                logger.info(f"Frame: {frame_idx} / {total_frames}")
        
        writer.close()
        elapsed = time.perf_counter() - start_time
        fps_render = total_frames / elapsed if elapsed > 0 else 0
        logger.info(f"Render done: {output_path}")
        logger.info(f"\tTotal time: {format_duration(elapsed)}")
        logger.info(f"\tSpeed: {fps_render:.1f} fps")
