import torch
from silicon_menagerie.utils import load_model, get_available_models, preprocess_image
from vision_model import VisionModel
import torch

class ImageNetVIT(VisionModel):    
    def __init__(self):
        model = load_model('dino_imagenet100_vitb14')
        super().__init__(model)
        self.model.eval()
        self.name = "imagenet_vit"
