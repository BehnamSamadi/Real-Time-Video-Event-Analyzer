"""
This module gets decoded streams and classifies them and sends results to result_manager
"""
from feature_extractor import FeatureExtractor
import faiss
import numpy as np


class Classifier(object):
    def __init__(self, vector_db_path=None, min_distance=0.6):
        self.feature_extractor = FeatureExtractor()
        self.index = self._load_vector_db(vector_db_path)
        self.min_distance = min_distance

    def _load_vector_db(self, vector_db_path):
        if vector_db_path:
            try:
                index = faiss.read_index(vector_db_path)
                return index
            except:
                print('Vector DB Read Error')
        vector_db_path = 'index_db.index'
        return self._init_vector_db(vector_db_path)

    def _init_vector_db(self, vector_db_path):
        dimention = 256
        quantizer = faiss.IndexFlatL2(dimention)
        index = faiss.IndexIVFFlat(
            quantizer, dimention, 100, faiss.METRIC_L2
        )
        x_train = np.random.random((10000, dimention)).astype('float32')
        x_train = x_train / np.sqrt(np.sum(x_train ** 2, -1, keepdims=True))
        index.train(x_train)
        self._save_index(vector_db_path)
        return index

    def predict(self, input):
        features = self.feature_extractor(input)
        distances, ids = self.index.search(features, 1)
        results = []
        for distance, id in zip(distances, ids):
            res = self.min_distance / (distance+1e-7) / 2
            conf = min(res, 1)
            results.append(conf)
        return results

    def _save_index(self, vector_db_path):
        assert self.index, 'Index not created'
        faiss.write_index(self.index, vector_db_path)

    def add_new_data(self, data, ids):
        assert len(data) == len(ids)
        features = self.feature_extractor(data)
        self.index.add_with_ids(features, ids)
    
    def clear_db(self):
        vector_db_path = 'index_db.index'
        self.index = self._init_vector_db(vector_db_path)

