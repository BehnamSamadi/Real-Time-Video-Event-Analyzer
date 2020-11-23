"""
This module Manages Results and saves them into DB
"""
from classifier import Classifier
import redis
import pickle


class ResultManager(object):
    def __init__(self, vector_db_path, in_queue_name, classifier_min_distance=0.6):
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
                conf = self.clf.predict([clip])
                self.send_status(index, conf)

    
    def deserialize_data(self, data):
        return pickle.loads(data[1])

    def send_status(self, index, conf):
        pass
    
    def update(self, dataset_path):
        pass