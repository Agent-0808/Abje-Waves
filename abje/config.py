"""配置参数"""

from dataclasses import dataclass, field
from enum import Enum


class NoteDuration(Enum):
    """音符时长"""
    WHOLE = "whole"           # 全音符
    HALF = "half"             # 二分音符
    QUARTER = "quarter"       # 四分音符
    EIGHTH = "eighth"         # 八分音符
    SIXTEENTH = "sixteenth"   # 十六分音符


@dataclass
class RenderConfig:
    """渲染配置"""
    width: int = 1280
    height: int = 720
    fps: int = 30
    output_dir: str = "output"
    output_name: str = "iriya"
    format: str = "mp4"  # "mov" 或 "mp4"

@dataclass
class ContentConfig:
    """内容配置"""
    bpm: int = 120
    default_speed: float = 0.3  # 屏幕宽度/秒
    max_radius_ratio: float = 1.5  # 相对屏幕宽度
    wave_duration: float = 3.0  # 秒
    interval: NoteDuration = NoteDuration.EIGHTH


@dataclass
class Config:
    """组合配置"""
    render: RenderConfig = field(default_factory=RenderConfig)
    content: ContentConfig = field(default_factory=ContentConfig)

    @property
    def width(self) -> int:
        return self.render.width

    @property
    def height(self) -> int:
        return self.render.height

    @property
    def fps(self) -> int:
        return self.render.fps

    @property
    def bpm(self) -> int:
        return self.content.bpm

    @property
    def default_speed(self) -> float:
        return self.content.default_speed

    @property
    def max_radius_ratio(self) -> float:
        return self.content.max_radius_ratio

    @property
    def wave_duration(self) -> float:
        return self.content.wave_duration

    def get_output_path(self) -> str:
        """获取完整输出路径"""
        return f"{self.render.output_dir}/{self.render.output_name}.{self.render.format}"

    def get_max_radius(self) -> int:
        """获取最大半径（像素）"""
        return int(self.max_radius_ratio * self.width)

    def seconds_per_beat(self) -> float:
        """每拍（四分音符）对应的秒数"""
        return 60.0 / self.bpm

    def seconds_for_duration(self, duration: NoteDuration) -> float:
        """指定音符时长对应的秒数"""
        multipliers = {
            NoteDuration.WHOLE: 4.0,
            NoteDuration.HALF: 2.0,
            NoteDuration.QUARTER: 1.0,
            NoteDuration.EIGHTH: 0.5,
            NoteDuration.SIXTEENTH: 0.25,
        }
        return self.seconds_per_beat() * multipliers[duration]

    def frames_per_beat(self) -> int:
        """每拍（四分音符）对应的帧数"""
        return int(self.fps * self.seconds_per_beat())

    def frames_for_duration(self, duration: NoteDuration) -> int:
        """指定音符时长对应的帧数"""
        return int(self.fps * self.seconds_for_duration(duration))
