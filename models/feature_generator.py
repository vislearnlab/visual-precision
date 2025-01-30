from abc import ABC, abstractmethod
import pandas as pd
import os
from typing import Dict, List, Optional, Tuple
import torch
from stimuli_loader import StimuliLoader
from torch.nn.functional import cosine_similarity

class FeatureGenerator(ABC):
    """Abstract base class for generating similarity scores between pairs of concepts."""
    
    def __init__(self, model, preprocess, device=None, name="feature_generator"):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        self.model = model.to(self.device)
        self.preprocess = preprocess
        self.name = name
        self.stimuli_loader = StimuliLoader()

    def similarity(self, embeddings1, embeddings2):
        # Compute cosine similarity
        similarity_score = cosine_similarity(embeddings1, embeddings2)
        return similarity_score.item()

    # Normalize each embedding to have a unit L2 norm
    def normalize_embeddings(self, embeddings):
        return [embedding / embedding.norm(dim=-1, keepdim=True) for embedding in embeddings]

    def save_similarities(self, sim_df: pd.DataFrame):
        """Save similarity scores to CSV."""
        self.stimuli_loader.save_df(sim_df, f'{self.name}_similarities.csv')

    @abstractmethod
    def similarities(self, stimulus1, stimulus2):
        """Compute similarity scores between two stimuli"""
        pass

    def format_similarity_row(self, word1, word2, similarity_score):
        return {'word1': word1, 'word2': word2, **similarity_score}

    def lookit_similarities(self):
        left_words, right_words = self.stimuli_loader.words()
        # Initialize a DataFrame for similarities
        similarity_data = []
        word_pair_set = set()
        # Populate the similarity DataFrame
        for word1, word2 in zip(left_words, right_words):
            pair = tuple(sorted([word1, word2]))  # Ensure consistent ordering (word1, word2)
            if pair not in word_pair_set:
                curr_similarities = self.similarities(word1, word2)
                if curr_similarities: 
                    similarity_data.append(self.format_similarity_row(word1, word2, curr_similarities))
                    word_pair_set.add(pair)
        # Create and save DataFrame
        similarity_df = pd.DataFrame(similarity_data)
        self.save_similarities(similarity_df)
        return similarity_df
