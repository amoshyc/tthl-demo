# Demo

## Requirements

在 `python 3.6` 下執行。

1. `ffmpeg`
2. `tensorflow`
3. `youtube-dl`
4. `pillow`
5. `numpy`
6. `tornado`

Except `ffmpeg`, others can be installed by

(Recommended executed in a virtual environment)

```
pip install -r requirements.txt
```

## Model Weights

1. [tensorflow object detection model (ssd_mobilenet_v1)](https://github.com/tensorflow/models/tree/master/research/object_detection)
2. weights of the model (it should be under `models/` already)

detection 的部份可以在安裝好 dependencies、編譯好 prototxt 後，將 `detection.py` 56~62 的註解拿掉，然後執行 `get_graph` 函式，程式就會去下載 model。

## Execution

Run `python server.py` and open `localhost:8080`