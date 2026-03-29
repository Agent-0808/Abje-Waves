"""配置参数"""

from dataclasses import dataclass
from enum import Enum


class NoteDuration(Enum):
    """音符时长"""
    WHOLE = "whole"           # 全音符
    HALF = "half"             # 二分音符
    QUARTER = "quarter"       # 四分音符
    EIGHTH = "eighth"         # 八分音符
    SIXTEENTH = "sixteenth"   # 十六分音符


@dataclass
class Config:
    """渲染配置"""
    width: int = 1920
    height: int = 1080
    fps: int = 60
    output_video: str = "output/Abje_waves.mov"
    
    bpm: int = 120
    
    default_speed: float = 0.3  # 屏幕宽度/秒
    default_color: tuple[int, int, int] = (70, 85, 254)
    max_radius_ratio: float = 1.5  # 相对屏幕宽度
    
    wave_duration: float = 3.0  # 秒
    
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
