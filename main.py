from abje import *

def main():
    config = Config(
        width=1280, height=720,
        bpm=90, fps=30,
        output_video="iriya.mov"
    )
    
    # 波纹参数编码
    texts = {
        EncodeType.SIDE: "鳥達は行方を消す",
        EncodeType.COLOR: "妄想の孵る季節迄",
        EncodeType.SPEED: "口約束を反芻して",
        EncodeType.BRIGHTNESS: "天啓と嘯きの中間",
        EncodeType.VERTICAL: "思惟の先で咲く華"
    }

    params_list = texts_to_wave_params(texts)
    
    renderer = Renderer(config)
    renderer.add_wave_params(params_list, interval=NoteDuration.EIGHTH)
    renderer.render()


if __name__ == "__main__":
    main()
