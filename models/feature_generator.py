from abc import ABC, abstractmethod
import itertools
import pandas as pd
import os
from typing import Dict, List, Optional, Tuple
import torch
from stimuli_loader import StimuliLoader
from torch.utils.data import DataLoader

from tqdm import tqdm
from torch.nn.functional import cosine_similarity
from dotenv import load_dotenv
load_dotenv()

class FeatureGenerator(ABC):
    """Abstract base class for generating similarity scores between pairs of concepts."""
    def __init__(self, model, preprocess, device=None, name="feature_generator", dataloader=None):
        # working with tversky CPU capacity
        torch.set_num_threads(1)
        if device is None:
            self.device = "cuda:1" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        self.model = model.to(self.device)
        self.preprocess = preprocess
        self.name = name
        # using default lookit stimuli
        self.dataloader = dataloader or StimuliLoader(
            dataset_file=os.path.join(
                os.environ.get("PROJECT_PATH"), "data", "metadata", "level-imagepair_data.csv"
            ),
            image_folder=os.path.join(
                os.environ.get("PROJECT_PATH"), "stimuli", "lookit", "exp1", "img"
            ),
            batch_size=1,
            stimuli_type="exp1"
        ).dataloader()
        self.image_word_alignment = lambda **x: self.model(**x).logits_per_image.softmax(dim=-1).detach().cpu().numpy()

    def similarity(self, embeddings1, embeddings2):
        # Compute cosine similarity
        similarity_score = cosine_similarity(embeddings1, embeddings2)
        return similarity_score.item()

    # Normalize each embedding to have a unit L2 norm
    def normalize_embeddings(self, embeddings):
        return [embedding / embedding.norm(dim=-1, keepdim=True) for embedding in embeddings]

    def save_similarities(self, sim_df: pd.DataFrame):
        """Save similarity scores to CSV."""
        self.save_df(sim_df, f'similarities-{self.name}_data.csv')

    @abstractmethod
    def similarities(self, stimulus1, stimulus2, dataloader_row):
        """Compute similarity scores between two stimuli"""
        pass

    def format_similarity_row(self, word1, word2, similarity_score):
        return {'word1': word1, 'word2': word2, **similarity_score}

    def lookit_similarities(self):
        """Calculate cosine similarities between all word pairs in the Lookit dataset"""
        text_set = set()
        similarity_data = []
        with torch.no_grad():
            for d in tqdm(self.dataloader, desc=f"Calculating {self.name} similarities"):
                for text1, text2 in itertools.combinations(d['text'], 2):
                    pair = tuple(sorted([text1, text2]))
                    if pair not in text_set:
                        curr_similarities = self.similarities(text1, text2, d)
                        similarity_data.append(self.format_similarity_row(text1, text2, curr_similarities))
                        text_set.add(pair)
        similarity_df = pd.DataFrame(similarity_data)
        self.save_similarities(similarity_df)
        return similarity_df

    def image_word_alignment(self, images, words):
        """Compute alignment between a set of images and a list of words"""
        inputs = self.preprocess(images=images, text=words, return_tensors="pt", padding=True)
        return self.image_word_alignment(**inputs)
    
    def save_df(self, df, filename):
        filepath = os.path.join(os.environ.get("PROJECT_PATH"), "data", "embeddings", filename)
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        if os.path.exists(filepath):
        # Read existing CSV and append new data if it belongs to a different epoch
        # TODO: change epoch to be a more variable field, add logging if dataframe is not being updated
            existing_df = pd.read_csv(filepath)
            if 'epoch' in existing_df.columns and 'epoch' in df.columns and not any(existing_df['epoch'].isin(df['epoch'])):
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df.to_csv(filepath, index=False)
            else:
                print(f"Dataframe {filename} exists, not updating")
        else:
            df.to_csv(filepath, index=False)
