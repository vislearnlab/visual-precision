import torch
import clip
from PIL import Image
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from torch.nn.functional import cosine_similarity
from dotenv import load_dotenv
import os
from multimodal_model import MultimodalModel
import pandas as pd

load_dotenv()

class CLIPGenerator(MultimodalModel):
    def __init__(self):
        self.model, self.preprocess = clip.load("ViT-B/32")
        super().__init__(self.model, self.preprocess)
        self.name = "clip"
    
    def preprocess_text(self, text):
        return clip.tokenize(f"a photo of a {text}").to(self.device)