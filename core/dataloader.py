import cv2
import glob as gb
import numpy as np


class VideoLoader(object):
    def __init__(self, data_path, frame_count):
        self.data_path = data_path
        self.video_list = gb.glob(data_path+'/*.mp4')
        self.frame_count = frame_count

    def __len__(self):
        return len(self.video_list)

    def __getitem__(self, index):
        sample = self.sample_from_video(self.video_list[index])
        return sample

    def sample_from_video(self, adress):
        cap = cv2.VideoCapture(adress)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if length < self.frame_count:
            return
        length_of_segment = np.floor(length/self.frame_count)
        sampled_frames = []
        for seg_number in range(self.frame_count):
            frame_number = seg_number * length_of_segment
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            _, frame = cap.read()
            sampled_frames.append(frame)
        return sampled_frames


