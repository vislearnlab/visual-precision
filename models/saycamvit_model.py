import torch
from silicon_menagerie.utils import load_model, preprocess_image
from vision_model import VisionModel
import torch

class SayCamVIT(VisionModel):    
    def __init__(self):
        torch.set_num_threads(1) 
        model = load_model('dino_say_vitb14')
        super().__init__(model)
        self.model.eval()
        self.name = "saycam_vit"
