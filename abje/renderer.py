"""视频渲染器"""

import os

import cv2
import imageio
import numpy as np

from .config import Config, NoteDuration
from .wave import Wave


class Renderer:
    """视频渲染器"""
    
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.waves: list[Wave] = []
    
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
        interval: NoteDuration = NoteDuration.EIGHTH,
        start_time: float = 0.0,
    ) -> None:
        """添加波纹参数列表，自动计算时间间隔"""
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
    
    def render(self, total_frames: int | None = None) -> None:
        """渲染视频"""
        if total_frames is None:
            total_frames = self.calculate_total_frames()
        
        width, height = self.config.width, self.config.height
        max_radius = self.config.get_max_radius()
        fps = self.config.fps
        
        output_dir = os.path.dirname(self.config.output_video)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        writer = imageio.get_writer(
            self.config.output_video,
            fps=fps,
            format='FFMPEG',
            codec='prores_ks',
            pixelformat='yuva444p10le',
            macro_block_size=None,
            output_params=['-profile:v', '4444']
        )
        
        print("Start rendering...")
        
        # 在循环外预分配内存
        canvas_rgba = np.zeros((height, width, 4), dtype=np.float32)
        temp_layer = np.zeros((height, width, 4), dtype=np.float32)
        
        for frame_idx in range(total_frames):
            current_time = frame_idx / fps
            canvas_rgba.fill(0)
            
            for wave in self.waves:
                if wave.time_start > current_time:
                    continue
                
                if not wave.is_alive_at_time(current_time, max_radius):
                    continue
                
                fade_factor = wave.get_fade_factor_at_time(current_time, max_radius)
                if fade_factor <= 0:
                    continue
                
                color_rgba = wave.get_color_with_brightness(fade_factor)
                radius = wave.get_radius_at_time(current_time)
                
                temp_layer.fill(0)
                # 画锐利的圆，并开启抗锯齿(LINE_AA)让效果更平滑
                cv2.circle(
                    temp_layer,
                    (wave.x, wave.y),
                    int(radius),
                    color=color_rgba,
                    thickness=wave.thickness * 2,
                    lineType=cv2.LINE_AA 
                )
                
                # 先做加法混合，不在这里做模糊
                canvas_rgba += temp_layer
            
            # 每帧只做一次模糊
            if np.any(canvas_rgba): 
                cv2.GaussianBlur(canvas_rgba, (31, 31), 0, dst=canvas_rgba)

            frame_out = np.clip(canvas_rgba, 0, 255).astype(np.uint8)
            writer.append_data(frame_out)
            
            if frame_idx % 20 == 0:
                print(f"Frame: {frame_idx} / {total_frames}")
        
        writer.close()
        print(f"Render {self.config.output_video} Done")