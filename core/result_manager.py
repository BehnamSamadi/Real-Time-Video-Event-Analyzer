"""
This module Manages Results and saves them into DB
"""
from classifier import Classifier
import redis
import pickle
import datetime
import time
import os
from dataloader import VideoLoader


class ResultManager(object):
    def __init__(self, app, classifier, in_queue_name):
        self.app = app
        self.queue = redis.Redis()
        self.status_db = redis.Redis(host='localhost', db=1)
        self.status_db.set('is_training', 0)
        self.in_queue_name = in_queue_name
        self.clf = classifier
        self.PIPELINE_FLAG = True
    
    def run(self):
        while self.PIPELINE_FLAG:
            # train_status = int(self.status_db.get('is_training'))
            train_status = self.clf.is_training()
            if not train_status:
                packed_data = self.queue.blpop([self.in_queue_name], 0)
                if packed_data is not None:
                    data = self.deserialize_data(packed_data)
                    index = data['index']
                    clip = data['data']
                    datetime = data['datetime']
                    while self.clf.is_training():
                        time.sleep(1)
                    conf = self.clf.predict(clip)
                    self.send_status(index, datetime, conf)
    
    def deserialize_data(self, data):
        return pickle.loads(data[1])

    def send_status(self, index, datetime, conf):
        res = {
            'datetime': datetime,
            'stream_id': index,
            'confidence': conf
        }
        print(res)
        self.app.send_task('backend.update_stream_status', (res,))

