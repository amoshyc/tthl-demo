import os
import tarfile
import zipfile
import shutil
import pathlib
from math import floor, ceil
from collections import defaultdict
from io import StringIO
import sys
sys.path.append('./object_detection')

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import skimage
from skimage import io
from skimage import draw
from skimage import transform

import six.moves.urllib as urllib
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from tqdm import tqdm


def crop(x, bbox):
    y1 = floor(224 * bbox[0])
    x1 = floor(224 * bbox[1])
    y2 = ceil(224 * bbox[2])
    x2 = ceil(224 * bbox[3])
    img = x[y1:y2, x1:x2]
    img = transform.resize(img, (100, 50), mode='reflect')
    return img


def draw_bbox(x, bbox):
    y1 = floor(224 * bbox[0])
    x1 = floor(224 * bbox[1])
    y2 = ceil(224 * bbox[2])
    x2 = ceil(224 * bbox[3])
    yy, cc = draw.polygon_perimeter(
        [y1, y1, y2, y2], [x1, x2, x2, x1], shape=x.shape, clip=True)
    x[yy, cc, :] = (255, 165, 0)


def get_graph():
    MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
    MODEL_FILE = MODEL_NAME + '.tar.gz'
    DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

    PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
    NUM_CLASSES = 90

    # opener = urllib.request.URLopener()
    # opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
    # tar_file = tarfile.open(MODEL_FILE)
    # for file in tar_file.getmembers():
    #     file_name = os.path.basename(file.name)
    #     if 'frozen_inference_graph.pb' in file_name:
    #         tar_file.extract(file, os.getcwd())

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    return detection_graph


def find_players(xs, out_dir='./result/players'):
    out_dir = pathlib.Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(str(out_dir))
    out_dir.mkdir()

    detection_graph = get_graph()
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            detection_boxes = detection_graph.get_tensor_by_name(
                'detection_boxes:0')
            detection_scores = detection_graph.get_tensor_by_name(
                'detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name(
                'detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name(
                'num_detections:0')

        players1 = []
        players2 = []
        none = np.zeros((100, 50, 3), dtype=np.uint8)

        for i, x in enumerate(tqdm(xs, ascii=True)):
            x = x.astype(np.uint8)
            (boxes, scores, classes, num) = sess.run(
                [
                    detection_boxes, detection_scores, detection_classes,
                    num_detections
                ],
                feed_dict={image_tensor: np.expand_dims(x, axis=0)})

            person_indices = classes == 1  # person
            score_indices = scores > 0.50
            indices = person_indices & score_indices
            boxes = boxes[indices]
            scores = scores[indices]
            classes = classes[indices]
            num = indices.sum()

            p1_img = none
            p2_img = none
            if num == 1:
                p1_img = crop(x, boxes[0])
            if num == 2:
                p1_img = crop(x, boxes[0])
                p2_img = crop(x, boxes[1])
            players1.append(p1_img)
            players2.append(p2_img)

            img = x.copy()
            if num == 1:
                draw_bbox(img, boxes[0])
            if num == 2:
                draw_bbox(img, boxes[0])
                draw_bbox(img, boxes[1])
            io.imsave(str(out_dir / f'{i:02d}.jpg'), img)

    del detection_graph
    return np.array(players1), np.array(players2)


if __name__ == '__main__':
    frame_folder = pathlib.Path('./result/frames')
    img_paths = sorted(list(frame_folder.iterdir()))
    xs = np.zeros((len(img_paths), 224, 224, 3), dtype=np.float32)
    for i, img_path in enumerate(img_paths):
        img = Image.open(img_path)
        img = img.resize((224, 224))
        xs[i] = np.array(img)

    find_players(xs, './result/players')