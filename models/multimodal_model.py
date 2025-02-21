from abc import ABC, abstractmethod
import itertools
from feature_generator import FeatureGenerator
import torch
import os
from PIL import Image
import numpy as np

class MultimodalModel(FeatureGenerator):
    """Abstract base class for multimodal models like CLIP and CVCL that extends FeatureGenerator"""
    
    def __init__(self, model, preprocess, dataloader=None, device=None):
        super().__init__(model, preprocess, dataloader, device)

    # Load and preprocess images
    def preprocess_image(self, image):
        return self.preprocess(image).unsqueeze(0).to(self.device)

    def preprocess_text(self, text):
        return self.model.tokenize(text).to(self.device)

    def encode_image(self, image):
        return self.model.encode_image(image)

    def encode_text(self, text):
        return self.model.encode_text(text)

    def image_embeddings(self, images):
        """Get image embeddings"""
        images = [self.preprocess_image(image) for image in images]
        with torch.no_grad():
            embeddings = [self.encode_image(image) for image in images]
        return self.normalize_embeddings(embeddings)

    def text_embeddings(self, words):
        """Get text embeddings"""
        all_text_features = [self.preprocess_text(word) for word in words]
        with torch.no_grad():
            embeddings = [self.encode_text(text_features) for text_features in all_text_features]
        return self.normalize_embeddings(embeddings)

    def multimodal_embeddings(self, image_embeddings, text_embeddings):
        """Get multimodal embeddings: by default, averages image and text embeddings"""
        return [(a + b) / 2 for a, b in zip(image_embeddings, text_embeddings)]

    def similarities(self, word1, word2, dataloader_row):
        valid_images = [img for img in dataloader_row['images'] if img is not None]
        # TODO: this only returns the similarity scores for the first pair of images: need to separate out, indexing is weird
        for image1, image2 in itertools.combinations(valid_images, 2):
            curr_image_embeddings = self.image_embeddings([image1, image2])
            curr_text_embeddings = self.text_embeddings([word1, word2])
            curr_multimodal_embeddings = self.multimodal_embeddings(curr_image_embeddings, curr_text_embeddings)
            similarity_scores = {
                'image_similarity': self.similarity(curr_image_embeddings[0], curr_image_embeddings[1]),
                'text_similarity': self.similarity(curr_text_embeddings[0], curr_text_embeddings[1]),
                'multimodal_similarity': self.similarity(curr_multimodal_embeddings[0], curr_multimodal_embeddings[1])
            }
            return similarity_scores
        print(f"skipping {word1} and {word2} since they do not have valid images")
        return {
        'image_similarity': None,
        'text_similarity': None,
        'multimodal_similarity': None
        }

    def normalize_embeddings(self, embeddings):
        """Normalize embeddings to unit L2 norm"""
        return [embedding / embedding.norm(dim=-1, keepdim=True) for embedding in embeddings]
    
