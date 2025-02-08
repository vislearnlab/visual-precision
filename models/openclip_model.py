import clip
from multimodal_model import MultimodalModel

class OpenCLIPGenerator(MultimodalModel):
    def __init__(self, model, preprocess, epoch=0):
        model.eval()
        super().__init__(model, preprocess)
        self.name = "openclip"
        self.epoch = epoch
    
    def preprocess_text(self, text):
        return clip.tokenize(f"a photo of a {text}").to(self.device)

    def format_similarity_row(self, word1, word2, similarity_score):
        return {'word1': word1, 'word2': word2, 'epoch': self.epoch, **similarity_score}
