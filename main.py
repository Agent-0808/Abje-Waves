from abje import *


def eucjp(text: str) -> list[int]:
    """自定义编码"""
    encoded = text.encode("euc-jp")
    bits = []
    for byte in encoded:
        for i in range(7, -1, -1):
            bit = -(byte >> i) & 1
            bits.append(bit)
    return bits

abje_str = "でぐちはすぐそこ"

def main():
    config = Config(
        render=RenderConfig(
            width=1280,
            height=720,
            fps=30,
            output_name="iriya",
            format="mp4",
        ),
        content=ContentConfig(bpm=90),
    )

    # 波纹参数编码
    codes = WaveCodes(
        side="鳥達は行方を消す",
        color="妄想の孵る季節迄",
        speed=("口約束を反芻して", eucjp), # 使用自定义编码函数
        brightness="天啓と嘯きの中間",
        vertical="思惟の先で咲く華"
    )

    params_list = codes_to_wave_params(codes)

    renderer = Renderer(config)
    renderer.add_wave_params(params_list)
    renderer.render()


if __name__ == "__main__":
    main()
