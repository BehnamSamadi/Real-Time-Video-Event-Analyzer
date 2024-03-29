"""
This module decodes Video Streams and Sending decoded frames to Redis queue for processing
"""
from celery import Task
import os
import numpy as np
import cv2
import time
import pickle
import redis
import datetime
from celery_app import app
from billiard.exceptions import Terminated
import threading
from uuid import uuid4


class Stream(Task):
    name = 'Stream'
    throws = (Terminated,)
    CAPTURE_FLAG = True
    redis_queue_host = os.getenv('REDIS_QUEUE_HOST', 'localhost')
    redis_queue_core_db = int(os.getenv('REDIS_QUEUE_CORE_DB', 0))
    redis_queue_db = int(os.getenv('REDIS_QUEUE_DB', 1))
    redis_db = redis.Redis(host=redis_queue_host, db=redis_queue_db)
    queue = None
    queue_name = None
    index = None
    sample_duration = None
    buffer = []
    sample_size = 32
    frame_size = (256, 256)
    active_delay = 1
    last_capture = -1
    sensitivity = 0
    sample_rate = 0
    last_active = -100
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    save_dir = './saved_clips/videos/saved_clips/'


    def run(self, index, stream_address, queue_name, sample_duration,
            sample_size, frame_size, active_delay=1, sensitivity=0.5):
        self.cap = self._create_stream(stream_address)
        self.queue = redis.Redis(host=self.redis_queue_host, db=self.redis_queue_core_db)
        self.redis_db.set(index, 1)
        self.queue_name = queue_name
        self.index = index
        self.sample_size = sample_size
        self.frame_size = frame_size
        self.active_delay = active_delay
        self.sensitivity = sensitivity
        self.sample_rate = sample_duration / sample_size

        while self.CAPTURE_FLAG:
            self.CAPTURE_FLAG = int(self.redis_db.get(self.index))
            self._sample()
            if self._is_active():
                self._send_to_queue()

    def _sample(self):
        if self.cap.isOpened:
            ret, frame = self.cap.read()
            if ret:
                if time.time() - self.last_capture >= self.sample_rate:
                    frame = cv2.resize(frame, self.frame_size)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.buffer.append(frame)
                    self.last_capture = time.time()
                if len(self.buffer) > self.sample_size:
                    self.buffer.pop(0)


    def _create_stream(self, stream_address):
        cap = cv2.VideoCapture(stream_address)
        return cap

    def _dump(self):
        data = np.array(self.buffer)
        index = self.index
        clip_id = str(uuid4())
        data_dict = {'data': data,
            'index': index,
            'datetime': datetime.datetime.now(),
            'id': clip_id
            }
        self.write_buffer(clip_id)
        return pickle.dumps(data_dict)

    def _send_to_queue(self):
        print('dumping')
        data = self._dump()
        self.queue.rpush(self.queue_name, data)
        self.last_active = time.time()

    def _is_active(self):
        if len(self.buffer) < self.sample_size:
            return False
        if time.time() - self.last_active > self.active_delay:
            std = np.std(self.buffer, axis=0) / 255 / 2
            norm_std = std.sum() / std.size
            if norm_std > self.sensitivity:
                return True
        return False

    def write_buffer(self, clip_id):
        video_path = self.save_dir + clip_id + '.mp4'
        video_writer = cv2.VideoWriter(video_path, self.fourcc, 1/self.sample_rate, self.frame_size)
        for frame in self.buffer:
            video_writer.write(frame[...,::-1])
        video_writer.release()
    

app.register_task(Stream())
