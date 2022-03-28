"""
This module gets decoded streams and classifies them and sends results to result_manager
"""
from feature_extractor import FeatureExtractor
import faiss
import numpy as np
import time


class Classifier(object):
    def __init__(self, vector_db_path='index_db.index', min_distance=0.6):
        self.feature_extractor = FeatureExtractor('i3d_resnet50_v1_feat.yaml')
        self.vector_db_path = vector_db_path
        self.index = self._load_vector_db()
        self.min_distance = min_distance
        self._training = False
        self._in_use = False

    def _load_vector_db(self):
        if self.vector_db_path:
            try:
                index = faiss.read_index(self.vector_db_path)
                return index
            except:
                print('Vector DB Read Error')
        self.vector_db_path = 'index_db.index'
        return self._init_vector_db()

    def _init_vector_db(self):
        self._training = True
        dimention = 2048
        index = faiss.IndexFlatL2(dimention)
        self._save_index(index, self.vector_db_path)
        self._training = False
        return index

    def predict(self, input):
        features = self.feature_extractor.predict(input)
        # while self._training:
        #     time.sleep(0.5)
        distances, ids = self.index.search(features, 1)
        results = []
        for distance, id in zip(distances, ids):
            print(distance)
            res = (self.min_distance + 1e-6) / (distance+1e-7) / 2
            res = float(res)
            conf = min(res, 1)
            results.append(conf)
        return results

    def is_training(self):
        return self._training

    def is_in_use(self):
        return self._in_use

    def _save_index(self, index, vector_db_path):
        assert index, 'Index not created'
        faiss.write_index(index, vector_db_path)

    def add_new_data(self, data, ids=-1):
        if ids == -1:
            features = self.feature_extractor.predict(data)
            self.index.add(features)
            # return
        # assert len(data) == len(ids)
        # features = self.feature_extractor(data)
        # self.index.add_with_ids(features, ids)
        self._save_index(self.index, self.vector_db_path)
    
    def clear_db(self):
        self.index.reset()
        # self.index = self._init_vector_db()