import shutil
import pathlib
import subprocess

import youtube_dl
import numpy as np
from PIL import Image
import tensorflow as tf

class Video(object):
    def __init__(self,
                 output_path='./hl.mp4',
                 frame_dir='./frames/',
                 start_time='00:00:00',
                 duration='00:00:30',
                 fps=1):
        self.input_path = ''
        self.output_path = output_path
        self.frame_dir = frame_dir
        self.start_time = start_time
        self.duration = duration
        self.fps = fps

    def __get_input_path(self, url):
        # download if necessary
        if pathlib.Path(url).exist():
            self.input_path = './video.mp4'
            self.__download(url)
        else:
            self.input_path = url

        ydl_opt = {
            'format': 'best[height<=480]',
            'outtmpl': self.input_path,
        } # yapf: disable
        with youtube_dl.YoutubeDL(ydl_opt) as ydl:
            ydl.download([url])

    def __write_frames(self):
        # ffmpeg -i out.mp4 -ss 00:00:00 -t duration -vf fps="fps=1" outfile
        self.frame_dir = self.input_path.parent
        if frame_dir.exist():
            shutil.rmtree(str(frame_dir))
        frame_dir.mkdir(parents=True, exist_ok=True)
        cmd = 'ffmpeg -i {} -ss {} -t {} -vf fps="fps={}" {}'.format(
            self.input_path, self.start_time, self.duration, self.fps,
            self.frame_dir / '%05d.jpg')
        subprocess.run(cmd, shell=True)

    def __load_frames(self):
        img_paths = list(self.frame_dir.iterdir())
        xs = np.zeros((len(img_paths, 224, 224)), dtype=np.float32)
        for i, img_path in enumerate(img_paths):
            img = Image.open(img_path)
            img.resize((224, 224))
            xs[i] = np.array(img)
        return xs

    def __predict(self, xs):
        model = load_model('')
        ys = model.predict(xs, batch_size=20)

        return ss, ee

    def __concat_video(self, ss, ee):
        # ffmpeg -i test.mp4
        # -filter_complex "\
        #   [0]trim=1:10,setpts=PTS-STARTPTS[v0]; \
        #   [0]trim=10:20,setpts=PTS-STARTPTS[v1]; \
        #   [v0][v1]concat=n=2[out]"
        # -map [out] out.mp4

        # assert len(ss) == len(ee), 'number of ss != number of ee'
        # for s, e in zip(ss, ee):
        #     assert s <= e, f'start({s}) should be <= end({e})'

        n = len(ss)
        inputs = [
            f'[0]trim={ss[i]}:{ee[i]},setpts=PTS-STARTPTS[v{i}]'
            for i in range(n)
        ]
        streams = ''.join([f'[v{i}]' for i in range(n)])
        concat = f'concat=n={n}[out]'
        filter_cmd = ';'.join([*inputs, streams + concat])
        cmd = 'ffmpeg -i {} -filter_complex "{}" -map [out] {} -y'.format(
            self.infile_path, filter_cmd, self.output_path)
        subprocess.run(cmd, shell=True)

    def highlight(self, url):
        self.__get_input_path()
        self.__write_frames()
        xs = self.__load_frames()
        ss, ee = self.__predict(xs)
        self.__concat_video(ss, es)


if __name__ == '__main__':
    Video().highlight('https://www.youtube.com/watch?v=D2gIt7WSY5Q')
