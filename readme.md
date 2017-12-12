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
2. weights of the model (played it under `models/`)

## Execution

Run `python server.py` and open `localhost:8080`