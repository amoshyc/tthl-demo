import shutil
import pathlib
import subprocess

import youtube_dl
import numpy as np
from PIL import Image
import tensorflow as tf


class Video(object):
    def __init__(self,
                 output_path='./static/hl.mp4',
                 frame_dir='./static/frames/',
                 start_time='00:00:00',
                 duration='00:00:30',
                 fps=1):
        self.input_path = None
        self.output_path = pathlib.Path(output_path)
        self.frame_dir = pathlib.Path(frame_dir)
        self.start_time = start_time
        self.duration = duration
        self.fps = fps

    def __get_input_path(self, url):
        # download if it's a web url
        if url.startswith('https://') or url.startswith('http://'):
            self.input_path = pathlib.Path('./video.mp4')
            if self.input_path.exists():
                self.input_path.unlink()
            cmd = f'youtube-dl -f "best[height<=480]" -o {self.input_path} {url}'
            subprocess.check_output(cmd, shell=True)
        else:
            self.input_path = pathlib.Path(url)

    def __write_frames(self):
        # ffmpeg -i out.mp4 -ss 00:00:00 -t duration -vf fps="fps=1" outfile
        if self.frame_dir.exists():
            shutil.rmtree(str(self.frame_dir))
        self.frame_dir.mkdir(parents=True, exist_ok=True)
        cmd = 'ffmpeg -i {} -ss {} -t {} -vf fps="fps={}" {} -loglevel panic -hide_banner'.format(
            self.input_path, self.start_time, self.duration, self.fps,
            self.frame_dir / '%05d.jpg')
        subprocess.run(cmd, shell=True)

    def __load_frames(self):
        img_paths = list(self.frame_dir.iterdir())
        xs = np.zeros((len(img_paths), 224, 224, 3), dtype=np.float32)
        for i, img_path in enumerate(img_paths):
            img = Image.open(img_path)
            img = img.resize((224, 224))
            xs[i] = np.array(img)
        return xs

    def __predict(self, xs):
        n_samples = xs.shape[0]
        model = tf.keras.models.load_model('models/vgg16_0.846_29.h5')
        pred = model.predict(xs, batch_size=15, verbose=1)
        pred = np.round(pred).astype(np.uint8).ravel()
        print(pred)

        itv = 6
        for i in range(n_samples - itv):
            s, t = i, i + itv
            if pred[s] == 1 and pred[t - 1] == 1:
                pred[s:t] = 1
        print(pred)

        ss, ee = [], []
        s, t = 0, -1
        while True:
            s = t + 1
            while s < n_samples and pred[s] == 0:
                s += 1
            if s >= n_samples:
                break
            t = s
            while t < n_samples and pred[t] == 1:
                t += 1
            ss.append(s)
            ee.append(t)
            if t >= n_samples:
                break

        return ss, ee

    def __concat_video(self, ss, ee):
        # Command for concat 2 segments
        # ffmpeg -i video.mp4 -filter_complex "\
        # [0:v]trim=1:10,setpts=PTS-STARTPTS[v0]; \
        # [0:a]atrim=1:10,asetpts=PTS-STARTPTS[a0]; \
        # [0:v]trim=10:20,setpts=PTS-STARTPTS[v1]; \
        # [0:a]atrim=10:20,asetpts=PTS-STARTPTS[a1]; \
        # [v0][a0][v1][a1]concat=n=2:v=1:a=1[outv][outa]" -map [outv] -map [outa] out.mp4
        n_segments = len(ss)
        trims = ''.join([
            f'[0:v]trim={ss[i]}:{ee[i] + 0.5},setpts=PTS-STARTPTS[v{i}];' + \
            f'[0:a]atrim={ss[i]}:{ee[i] + 0.5},asetpts=PTS-STARTPTS[a{i}];'
            for i in range(n_segments)
        ])
        concat = \
            ''.join([f'[v{i}][a{i}]' for i in range(n_segments)]) + \
            f'concat=n={n_segments}:v=1:a=1[outv][outa]'
        cmd = \
            f'ffmpeg -y -i {self.input_path} -filter_complex "{trims}{concat}" -map [outv] -map [outa] "{self.output_path}" -loglevel panic -hide_banner'
        print(cmd)
        subprocess.run(cmd, shell=True)

    def highlight(self, url):
        print('*' * 50)
        print('Downloading')
        print('*' * 50)
        self.__get_input_path(url)

        print('*' * 50)
        print('Writing Frames')
        print('*' * 50)
        self.__write_frames()

        print('*' * 50)
        print('Loading Frames')
        print('*' * 50)
        xs = self.__load_frames()

        print('*' * 50)
        print('Predicting')
        print('*' * 50)
        ss, ee = self.__predict(xs)

        print('*' * 50)
        print('Generating Highlight')
        print('*' * 50)
        self.__concat_video(ss, ee)


if __name__ == '__main__':
    Video().highlight(
        'https://www.youtube.com/watch?v=VLe_FKIl9qY&list=PLVAOVDY2mEaH3ovJDmWw2-su5gR6AKpiS&t=23s&index=2'
    )
