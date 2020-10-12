import numpy as np



class FeatureExtractor:
    def __init__(self):
        """Some model initializations here"""
        self.feature_size = 256


    def __call__(self, frames):
        """Feature Extractions here"""
        features = np.random.random((1, self.feature_size))
        features = np.sqrt(np.sum(features ** 2, -1, keepdims=True))
        return features

