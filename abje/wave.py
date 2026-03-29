"""波纹类"""

from dataclasses import dataclass, field

from .config import Config


@dataclass
class Wave:
    """单个波纹"""
    side: str                                      # "left" 或 "right"
    time_start: float = 0.0                        # 开始时间 (秒)
    speed_factor: float = 1.0                      # 速度系数 (相对于基准速度)
    color: tuple[int, int, int] = (100, 150, 255)  # RGB 颜色
    thickness: int = 10                            # 线条粗细
    brightness: float = 1.0                        # 亮度 (0.0 - 1.0)
    vertical_pos: float = 0.5                      # 垂直位置 (0.0=下, 1.0=上)
    
    _config: Config = field(default_factory=Config, repr=False)
    _x: int = field(default=0, init=False, repr=False)
    _y: int = field(default=0, init=False, repr=False)
    
    def __post_init__(self):
        self._x = 0 if self.side == "left" else self._config.width
        self._y = int(self._config.height * (1 - self.vertical_pos))
    
    @property
    def x(self) -> int:
        return self._x
    
    @property
    def y(self) -> int:
        return self._y
    
    def get_radius_at_time(self, current_time: float) -> float:
        """获取指定时间的半径（像素）"""
        if current_time < self.time_start:
            return 0.0
        elapsed = current_time - self.time_start
        actual_speed = self._config.default_speed * self.speed_factor * self._config.width
        return actual_speed * elapsed
    
    def is_alive_at_time(self, current_time: float, max_radius: int) -> bool:
        """检查波纹在指定时间是否仍然可见"""
        return self.get_radius_at_time(current_time) < max_radius
