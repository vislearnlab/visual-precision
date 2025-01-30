from abc import ABC, abstractmethod
from feature_generator import FeatureGenerator
import torch
import os
from PIL import Image
import numpy as np

class MultimodalModel(FeatureGenerator):
    """Abstract base class for multimodal models like CLIP and CVCL that extends FeatureGenerator"""
    
    def __init__(self, model, preprocess, device=None):
        super().__init__(model, preprocess, device)
        self.image_word_alignment = lambda **x: self.model(**x).logits_per_image.softmax(dim=-1).detach().cpu().numpy()

    # Load and preprocess images
    def preprocess_image(self, image_path):
        image = Image.open(image_path).convert("RGB")
        return self.preprocess(image).unsqueeze(0).to(self.device)

    def preprocess_text(self, text):
        return self.model.tokenize(text).to(self.device)

    def encode_image(self, image):
        return self.model.encode_image(image)

    def encode_text(self, text):
        return self.model.encode_text(text)

    def image_embeddings(self, image_paths):
        """Get image embeddings"""
        images = [self.preprocess_image(image_path) for image_path in image_paths]
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

    def similarities(self, word1, word2):
        image1 = self.stimuli_loader.word_to_image(word1)
        image2 = self.stimuli_loader.word_to_image(word2)
        # If either images are not found, return None
        if image1 is None or image2 is None:
            return None
        curr_image_embeddings = self.image_embeddings([image1, image2])
        curr_text_embeddings = self.text_embeddings([word1, word2])
        curr_multimodal_embeddings = self.multimodal_embeddings(curr_image_embeddings, curr_text_embeddings)
        similarity_scores = {
            'image_similarity': self.similarity(curr_image_embeddings[0], curr_image_embeddings[1]),
            'text_similarity': self.similarity(curr_text_embeddings[0], curr_text_embeddings[1]),
            'multimodal_similarity': self.similarity(curr_multimodal_embeddings[0], curr_multimodal_embeddings[1])
        }
        print(f"{word1} and {word2} similarity scores: {similarity_scores}")
        return similarity_scores

    def normalize_embeddings(self, embeddings):
        """Normalize embeddings to unit L2 norm"""
        return [embedding / embedding.norm(dim=-1, keepdim=True) for embedding in embeddings]

    def image_word_alignment(self, images, words):
        """Compute alignment between a set of images and a list of words"""
        inputs = self.preprocess(images=images, text=words, return_tensors="pt", padding=True)
        return self.image_word_alignment(**inputs)
