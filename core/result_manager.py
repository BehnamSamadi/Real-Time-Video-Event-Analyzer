"""
This module Manages Results and saves them into DB
"""
from classifier import Classifier
import redis
import pickle
import datetime
import time
from dataloader import VideoLoader


class ResultManager(object):
    def __init__(self, app, vector_db_path, in_queue_name, classifier_min_distance=0.6):
        self.app = app
        self.queue = redis.Redis()
        self.in_queue_name = in_queue_name
        self.clf = Classifier(vector_db_path, classifier_min_distance)
        self.PIPELINE_FLAG = True
    
    def run(self):
        while self.PIPELINE_FLAG:
            packed_data = self.queue.blpop([self.in_queue_name], 0)
            if packed_data is not None:
                data = self.deserialize_data(packed_data)
                index = data['index']
                clip = data['data']
                datetime = data['datetime']
                while self.clf.is_training():
                    time.sleep(1)
                conf = self.clf.predict([clip])
                self.send_status(index, datetime, conf)
    
    def deserialize_data(self, data):
        return pickle.loads(data[1])

    def send_status(self, index, datetime, conf):
        res = {
            'datetime': datetime,
            'cam_index': index,
            'confidence': conf
        }
        print(res)
        self.app.send_task('backend.update_stream_status', (res,))
    
    def update(self, dataset_path):
        loader = VideoLoader(dataset_path, 8)
        self.clf.clear_db()
        for i in range(len(loader)):
            video = loader[i]
            if video:
                self.clf.add_new_data(video, -1)
