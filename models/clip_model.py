import clip
from dotenv import load_dotenv
from multimodal_model import MultimodalModel

load_dotenv()

class CLIPGenerator(MultimodalModel):
    def __init__(self, dataloader=None, device=None):
        self.model, self.preprocess = clip.load("ViT-B/32")
        super().__init__(self.model, self.preprocess, dataloader, device)
        self.name = "clip"
    
    def preprocess_text(self, text):
        return clip.tokenize(f"a photo of a {text}").to(self.device)
    