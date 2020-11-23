import numpy as np
from models import TSN
import torch


class FeatureExtractor:
    def __init__(self):
        """Some model initializations here"""
        weights = 'TRN_moments.pth.tar'
        num_classes = 339
        self.input_size = 224
        self.num_segments = 8
        self.img_feature_dim = 256
        self.consensus_type = "TRNmultiscale"
        self.base_arch = "InceptionV3"
        self.feature_size = 256
        self.modality = 'RGB'
        self.net = TSN(num_classes, self.num_segments,
                        self.modality, self.base_arch,
                        consensus_type=self.consensus_type,
                        print_spec=False)
        checkpoint = torch.load(weights)

        base_dict = {'.'.join(k.split('.')[1:]): v for k, v in list(checkpoint['state_dict'].items())}
        self.net.load_state_dict(base_dict)
        self.net.cuda().eval()


    def __call__(self, clips):
        """Feature Extractions here"""
        features = np.random.random((len(clips), self.feature_size))
        features = np.sqrt(np.sum(features ** 2, -1, keepdims=True))
        return features

