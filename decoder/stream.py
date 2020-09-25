"""
This module decodes Video Streams and Sending decoded frames to Redis queue for processing
"""
from celery import Task
import numpy as np
import cv2
import time
import pickle



class Stream(Task):

    capture_flag = True
    queue = None
    index = None
    sample_duration = None
    buffer = []
    sample_size = 10
    frame_size = (320, 240)
    active_delay = 1
    last_capture = -1
    sensitivity = 0
    sample_rate = 0
    last_active = -100


    def run(self, index, stream_address, queue, sample_duration,
            sample_size, frame_size, active_delay=1, sensitivity=0.5):
        
        self.cap = self._create_stream(stream_address)
        self.queue = queue
        self.index = index
        self.sample_size = sample_size
        self.active_delay = active_delay
        self.sensitivity = sensitivity
        self.sample_rate = sample_duration / sample_size
        while self.capture_flag:
            self._sample()
            if self._is_active():
                self._send_to_queue()


    def _sample(self):
        if cap.isOpened:
            ret, frame = self.cap.read()
            if ret:
                if time.time() - self.last_capture >= self.sample_rate:
                    frame = cv2.resize(frame, self.frame_size)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.buffer.append(frame)
                if len(self.buffer) > self.sample_size:
                    self.buffer.pop(0)


    def _create_stream(self, stream_address):
        cap = cv2.VideoCapture(stream_address)
        return cap

    def _dump(self):
        data = np.array(self.sample_buffer)
        index = self.index
        data_dict = {'data': data,
            'index': index}
        return pickle.dumps(data_dict)

    def _send_to_queue(self):
        data = self._dump()
        self.queue.rpush('queue:clips', data)

    def _is_active(self):
        if time.time - self.last_active > self.active_delay:
            std = np.std(sample_buffer, axis=0) / 255 / 2
            norm_std = std.sum() / std.size()
            if norm_std > self.sensitivity:
                return True
        return False
