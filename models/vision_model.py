import itertools
import torch
from feature_generator import FeatureGenerator
import torch
from torchvision import transforms as pth_transforms

# Abstract base class for CNNs or ViT-like transformers
class VisionModel(FeatureGenerator):    
    def __init__(self, model, preprocess=None, device=None):
        # using ViT-like transform
        preprocess = lambda img: pth_transforms.Compose([
            pth_transforms.Resize(1400),
            pth_transforms.ToTensor(),
            pth_transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])(img)
        super().__init__(model, preprocess, device)
    
    # Load and preprocess images
    def preprocess_image(self, image):
        return self.preprocess(image).unsqueeze(0).to(self.device)

    def preprocess_text(self, text):
        return self.model.tokenize(text).to(self.device)

    def encode_image(self, image):
        with torch.no_grad():
            return self.model(image)
        
    def image_embeddings(self, image_paths):
        """Get image embeddings"""
        images = [self.preprocess_image(image_path) for image_path in image_paths]
        with torch.no_grad():
            embeddings = [self.encode_image(image) for image in images]
        return self.normalize_embeddings(embeddings)

    def similarities(self, word1, word2, dataloader_row):
        # TODO: this only returns the similarity scores for the first pair of images: need to separate out, indexing is weird
        for image1, image2 in itertools.combinations(dataloader_row['images'], 2):
            curr_image_embeddings = self.image_embeddings([image1, image2])
            similarity_scores = {
                'image_similarity': self.similarity(curr_image_embeddings[0], curr_image_embeddings[1]),
            }
            return similarity_scores

    def normalize_embeddings(self, embeddings):
        """Normalize embeddings to unit L2 norm"""
        return [embedding / embedding.norm(dim=-1, keepdim=True) for embedding in embeddings]
