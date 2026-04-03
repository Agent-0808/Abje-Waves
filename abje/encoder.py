"""编码转换功能"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, TypeAlias


class EncodeType(Enum):
    """编码类型"""
    SIDE = "side"               # [左:0/右:1] → 波纹位置
    COLOR = "color"             # [青:0/緑:1] → 波纹颜色
    SPEED = "speed"             # [遅:0/速:1] → 波纹速度
    BRIGHTNESS = "brightness"   # [暗:0/明:1] → 波纹亮度
    VERTICAL = "vertical"       # [下:0/上:1] → 垂直位置


# 类型别名：文本输入源（字符串、二进制流、或带编码函数的元组）
TextSource: TypeAlias = str | list[int] | tuple[str, Callable[[str], list[int]]]


def _to_bits(value: TextSource, encoding: str = "euc-jp") -> list[int]:
    """统一转换为二进制流"""
    if isinstance(value, list):
        return value  # 直接是二进制流
    if isinstance(value, tuple):
        text, encoder = value
        return encoder(text)  # 使用自定义编码函数
    # 普通字符串，使用默认编码
    return encode_to_binary(value, encoding)


@dataclass
class WaveCodes:
    """波纹编码配置类"""

    side: TextSource | None = None
    color: TextSource | None = None
    speed: TextSource | None = None
    brightness: TextSource | None = None
    vertical: TextSource | None = None


ENCODE_MAPPINGS: dict[EncodeType, dict[int, dict]] = {
    EncodeType.SIDE: {
        0: {"side": 0.0},
        1: {"side": 1.0},
    },
    EncodeType.COLOR: {
        0: {"color": (100, 200, 255)},
        1: {"color": (100, 255, 150)},
    },
    EncodeType.SPEED: {
        0: {"speed_factor": 0.8},   # 慢速 = 0.8v
        1: {"speed_factor": 1.2},   # 快速 = 1.2v
    },
    EncodeType.BRIGHTNESS: {
        0: {"brightness": 0.7},
        1: {"brightness": 1.0},
    },
    EncodeType.VERTICAL: {
        0: {"vertical_pos": 0.47},
        1: {"vertical_pos": 0.53},
    },
}


def encode_to_binary(text: str, encoding: str = "euc-jp") -> list[int]:
    """将文本转换为二进制序列"""
    encoded = text.encode(encoding)
    bits = []
    for byte in encoded:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def binary_to_wave_params(bits: list[int], encode_type: EncodeType) -> list[dict]:
    """将二进制序列转换为波纹参数"""
    mapping = ENCODE_MAPPINGS[encode_type]
    return [mapping[bit].copy() for bit in bits]


def merge_wave_params(params_list: list[list[dict]]) -> list[dict]:
    """合并多个参数列表（同一组波纹的多个属性）"""
    if not params_list:
        return []
    
    count = max(len(p) for p in params_list)
    merged = []
    
    for i in range(count):
        wave_params = {}
        for params in params_list:
            if i < len(params):
                wave_params.update(params[i])
        merged.append(wave_params)
    
    return merged


def codes_to_wave_params(texts: WaveCodes, encoding: str = "euc-jp") -> list[dict]:
    """将波纹编码配置转换为合并后的波纹参数列表"""

    fields = {
        EncodeType.SIDE: texts.side,
        EncodeType.COLOR: texts.color,
        EncodeType.SPEED: texts.speed,
        EncodeType.BRIGHTNESS: texts.brightness,
        EncodeType.VERTICAL: texts.vertical,
    }

    all_params = []
    for encode_type, value in fields.items():
        if value is None:
            continue
        bits = _to_bits(value, encoding)
        params = binary_to_wave_params(bits, encode_type)
        all_params.append(params)

    return merge_wave_params(all_params)
