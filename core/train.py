"""
This module Manages Results and saves them into DB
"""
from classifier import Classifier
import redis
import pickle
import datetime
import time
from dataloader import VideoLoader


class ModelTrainer(object):
    def __init__(self, app, classifier):
        self.app = app
        self.status_db = redis.Redis(host='localhost', db=1)
        self.clf = classifier
    
    def train(self, dataset_path):
        # self.status_db.set('is_training', 1)
        self.clf._training = True
        while self.clf.is_in_use():
            print('waiting for inference...')
            time.sleep(0.1)
        loader = VideoLoader(dataset_path, 32)
        self.clf.clear_db()
        for i in range(len(loader)):
            video = loader[i]
            if video:
                self.clf.add_new_data(video, -1)
        self.clf._training = False
        self.status_db.set('is_training', 0)
