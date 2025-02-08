import torch
import clip
from PIL import Image
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from torch.nn.functional import cosine_similarity
from dotenv import load_dotenv
import os
import pandas as pd
from multimodal.multimodal_lit import MultiModalLitModel
from multimodal_model import MultimodalModel

load_dotenv()

class CVCLGenerator(MultimodalModel):
    def __init__(self):
        self.model, self.preprocess = MultiModalLitModel.load_model()
        super().__init__(self.model, self.preprocess)
        self.model.eval()
        self.name = "cvcl"
    
    def preprocess_text(self, text):
        texts, texts_len = self.model.tokenize(text)
        texts, texts_len = texts.to(self.device), texts_len.to(self.device)
        return texts, texts_len
    
    def text_embeddings(self, words):
        all_text_features = [self.preprocess_text(word) for word in words]
        with torch.no_grad():
            embeddings = [self.model.encode_text(text_features, text_lens) for text_features, text_lens in all_text_features]
        return self.normalize_embeddings(embeddings)
