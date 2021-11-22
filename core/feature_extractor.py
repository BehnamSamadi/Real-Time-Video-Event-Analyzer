from gluoncv.torch.model_zoo.action_recognition.i3d_resnet import i3d_resnet50_v1_kinetics400
from gluoncv.torch.engine.config import get_cfg_defaults
from gluoncv.torch.data.transforms.videotransforms import video_transforms, volume_transforms
import numpy as np
import torch


class FeatureExtractor(object):
    def __init__(self, config_file) -> None:
        super().__init__()
        cfg = get_cfg_defaults()
        cfg.merge_from_file(config_file)
        self.model = i3d_resnet50_v1_kinetics400(cfg)
        self.model.eval()

        self.data_resize = video_transforms.Compose([
                    video_transforms.Resize(size=(256), interpolation='bilinear')
                ])
        self.data_transform = video_transforms.Compose([
            volume_transforms.ClipToTensor(),
            video_transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                        std=[0.229, 0.224, 0.225])
        ])
    
    def predict(self, clip):
        clip = self.__do_transforms(clip)
        features = self.model(clip)
        return features

    def __do_transforms(self, frames):
        clip = self.data_resize(frames)
        clip = self.data_transform(clip)
        clip = np.stack([clip], 0)
        clip = torch.from_numpy(clip)
        return clip
