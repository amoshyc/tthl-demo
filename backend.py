import shutil
import pathlib
import subprocess

import youtube_dl
import numpy as np
from PIL import Image
import tensorflow as tf
import detection

class Video(object):
    def __init__(self,
                 output_path='./result/hl.mp4',
                 video_path='./result/v30.mp4',
                 frame_dir='./result/frames/',
                 start_time='00:00:11',
                 duration='00:00:30',
                 fps=1):
        self.input_path = None
        self.video_path = pathlib.Path(video_path)
        self.output_path = pathlib.Path(output_path)
        self.frame_dir = pathlib.Path(frame_dir)
        self.start_time = start_time
        self.duration = duration
        self.fps = fps

    def __get_input(self, url):
        # download if it's a web url
        if url.startswith('https://') or url.startswith('http://'):
            self.input_path = pathlib.Path('./raw.mp4')
            if self.input_path.exists():
                self.input_path.unlink()
            cmd = f'youtube-dl -f "best[height<=240]" --no-playlist -o "{self.input_path}" "{url}"'
            subprocess.check_output(cmd, shell=True)
        else:
            self.input_path = pathlib.Path(url)

    def __gen_video(self):
        # ffmpeg -i input.mp4 -ss 00:00:00 -t duration outfile
        if self.video_path.exists():
            self.video_path.unlink()
        cmd = 'ffmpeg -i "{}" -ss {} -t {} -loglevel panic -hide_banner "{}"'.format(
            self.input_path, self.start_time, self.duration, self.video_path)
        print(cmd)
        subprocess.run(cmd, shell=True)

        # ffmpeg -i input.mp4 -ss 00:00:00 -t duration -vf fps="fps=1" outfile
        if self.frame_dir.exists():
            shutil.rmtree(str(self.frame_dir))
        self.frame_dir.mkdir(parents=True, exist_ok=True)
        cmd = 'ffmpeg -i "{}" -ss {} -t {} -vf fps="fps={}" -loglevel panic -hide_banner "{}"'.format(
            self.input_path, self.start_time, self.duration, self.fps,
            self.frame_dir / '%05d.jpg')
        print(cmd)
        subprocess.run(cmd, shell=True)

    def __load_frames(self, folder):
        img_paths = sorted(list(folder.glob('*.jpg')))
        xs = np.zeros((len(img_paths), 224, 224, 3), dtype=np.float32)
        for i, img_path in enumerate(img_paths):
            img = Image.open(img_path)
            img = img.resize((224, 224))
            xs[i] = np.array(img)
        return xs

    def __predict(self, xs, p1, p2):
        n_samples = xs.shape[0]
        model = tf.keras.models.load_model('models/players_vgg19_0.876_23.h5', compile=False)
        pred = model.predict([xs, p1, p2], batch_size=15, verbose=1).flatten()
        print(pred)
        pred = (pred > 0.3).astype(np.uint8)
        print(pred)

        for itv in range(2, 6):
            for i in range(n_samples - itv):
                s, t = i, i + itv
                if pred[s] == 1 and pred[t - 1] > 0:
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

        return pred, ss, ee

    def __concat_segments(self, ss, ee):
        # Command for concat 2 segments
        # ffmpeg -i video.mp4 -filter_complex "\
        # [0:v]trim=1:10,setpts=PTS-STARTPTS[v0]; \
        # [0:a]atrim=1:10,asetpts=PTS-STARTPTS[a0]; \
        # [0:v]trim=10:20,setpts=PTS-STARTPTS[v1]; \
        # [0:a]atrim=10:20,asetpts=PTS-STARTPTS[a1]; \
        # [v0][a0][v1][a1]concat=n=2:v=1:a=1[outv][outa]" -map [outv] -map [outa] out.mp4
        # https://ffmpeg.org/ffmpeg-filters.html#concat
        n_segments = len(ss)
        trims = ''.join([
            f'[0:v]trim={ss[i]}:{ee[i] + 0.3},setpts=PTS-STARTPTS[v{i}];' + \
            f'[0:a]atrim={ss[i]}:{ee[i] + 0.3},asetpts=PTS-STARTPTS[a{i}];'
            for i in range(n_segments)
        ])
        concat = \
            ''.join([f'[v{i}][a{i}]' for i in range(n_segments)]) + \
            f'concat=n={n_segments}:v=1:a=1[outv][outa]'
        cmd = \
            f'ffmpeg -y -i "{self.video_path}" -filter_complex "{trims}{concat}" -loglevel panic -hide_banner -map [outv] -map [outa] "{self.output_path}"'
        print(cmd)
        subprocess.run(cmd, shell=True)

    def highlight(self, url):
        print('#', 'Getting Input')
        self.__get_input(url)

        print('#', 'Writing Frames')
        self.__gen_video()

        print('#', 'Loading Frames')
        xs = self.__load_frames(self.frame_dir)

        print('#', 'Finding Players')
        p1, p2 = detection.find_players(xs)

        print('#', 'Predicting')
        pred, ss, ee = self.__predict(xs, p1, p2)

        print('#', 'Generating Highlight')
        self.__concat_segments(ss, ee)

        print('#', 'Finished')
        return pred.tolist()

if __name__ == '__main__':
    # Video().highlight(
    #     'https://www.youtube.com/watch?v=SLJHRfudk6Q&index=2&list=PLVAOVDY2mEaEh8KT3TzYL_8or7yX80Ce7'
    # )
    Video().highlight('./raw.mp4')
