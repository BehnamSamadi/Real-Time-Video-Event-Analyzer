"""
This module gets decoded streams and classifies them and sends results to result_manager
"""
from feature_extractor import FeatureExtractor
import faiss
import numpy as np
import time


class Classifier(object):
    def __init__(self, vector_db_path='index_db.index', min_distance=0.6):
        self.feature_extractor = FeatureExtractor()
        self.vector_db_path = vector_db_path
        self.index = self._load_vector_db()
        self.min_distance = min_distance
        self._training = False

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
        dimention = 256
        quantizer = faiss.IndexFlatL2(dimention)
        index = faiss.IndexIVFFlat(
            quantizer, dimention, 100, faiss.METRIC_L2
        )
        x_train = np.random.random((10000, dimention)).astype('float32')
        x_train = x_train / np.sqrt(np.sum(x_train ** 2, -1, keepdims=True))
        index.train(x_train)
        self._save_index(index, self.vector_db_path)
        self._training = False
        return index

    def predict(self, input):
        features = self.feature_extractor(input)
        while self._training:
            time.sleep(0.5)
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

    def _save_index(self, index, vector_db_path):
        assert index, 'Index not created'
        faiss.write_index(index, vector_db_path)

    def add_new_data(self, data, ids):
        if ids == -1:
            features = self.feature_extractor(data)
            self.index.add(features)
            return
        assert len(data) == len(ids)
        features = self.feature_extractor(data)
        self.index.add_with_ids(features, ids)
    
    def clear_db(self):
        self.index = self._init_vector_db()