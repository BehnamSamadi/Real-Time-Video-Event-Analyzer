"""
This module Manages Results and saves them into DB
"""
import redis
import pickle
import time
import os
import requests
import json


BACKEND_ADDRESS = os.getenv('BACKEND_SEND_STATUS_URL', 'http://localhost:5000/update_status')


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
            packed_data = self.queue.blpop([self.in_queue_name], 0)
            if packed_data is not None:
                data = self.deserialize_data(packed_data)
                index = data['index']
                clip = data['data']
                datetime = data['datetime']
                while self.clf.is_training():
                    print('waiting for train...')
                    time.sleep(1)
                self.clf._in_use = True
                conf = self.clf.predict(clip)
                self.send_status(index, datetime, conf[0])
                self.clf._in_use = False
    
    def deserialize_data(self, data):
        return pickle.loads(data[1])

    def send_status(self, index, datetime, conf):
        print(type(datetime))
        stream_status = {
            'datetime': str(datetime),
            'stream_id': index,
            'confidence': conf
        }
        # stream_status = json.dumps(stream_status, indent=4, sort_keys=True)
        print(stream_status)
        requests.post(BACKEND_ADDRESS, json=stream_status)
