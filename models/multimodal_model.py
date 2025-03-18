from abc import ABC, abstractmethod
import itertools
from feature_generator import FeatureGenerator
import torch
import os
from PIL import Image
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_distances
from torch.nn.functional import cosine_similarity
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np

class MultimodalModel(FeatureGenerator):
    """Abstract base class for multimodal models like CLIP and CVCL that extends FeatureGenerator"""
    
    def __init__(self, model, preprocess, dataloader=None, device=None):
        super().__init__(model, preprocess, dataloader, device)
        self.image_word_alignment = lambda **x: self.model(**x).logits_per_image.softmax(dim=-1).detach().cpu().numpy()

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
    
    def text_to_images_logits(self, image_embeddings, text_embeddings, logit_scale=100):
        """Get logits of text to image embedding dot products"""
        return logit_scale * image_embeddings @ text_embeddings.t()
    
    def text_to_images_similarity(self, image_embeddings, text_embedding, logit_scale=100):
        # Convert image_embeddings list to tensor if needed
        if isinstance(image_embeddings, list):
            image_embeddings = torch.stack(image_embeddings)
        logits = self.text_to_images_logits(image_embeddings, text_embedding, logit_scale).to(self.device)
        softmaxes = torch.nn.functional.softmax(logits, dim=0)
        return softmaxes[1][0].item()
    
    def multimodal_luce(self, image_embeddings, text_embedding):
        target_similarity = self.similarity(image_embeddings[0], text_embedding)
        distractor_similarity = self.similarity(image_embeddings[1], text_embedding)
        luce = distractor_similarity / (distractor_similarity + target_similarity)
        return luce

    def similarities(self, word1, word2, images):
        valid_images = [img for img in images if img is not None]
        similarity_scores = []
        # TODO: this only returns the similarity scores for the first pair of images: need to separate out, indexing is weird
        for image1, image2 in itertools.combinations(valid_images, 2):
            curr_image_embeddings = self.image_embeddings([image1, image2])
            curr_text_embeddings = self.text_embeddings([word1, word2])
            # TODO: need to fix how each row is labeled in lookit_similarities, 
            similarity_scores.append({
                'image_similarity': self.similarity(curr_image_embeddings[0], curr_image_embeddings[1]),
                'text_similarity': self.similarity(curr_text_embeddings[0], curr_text_embeddings[1]),
                # finding distractor image to target word similarity
                'multimodal_similarity': self.text_to_images_similarity(curr_image_embeddings, curr_text_embeddings[0], logit_scale=10),
            })
        if similarity_scores == []:
            print(f"skipping {word1} and {word2} since they do not have valid images")
            return [{
                'image_similarity': None,
                'text_similarity': None,
                'multimodal_similarity': None
            }]
        else:
            return similarity_scores
        
    # TODO: probably move this to the dataloader row level instead of to a pair of words within a dataloader row
    # TODO: words or texts? what is my parameter
    def embeddings(self, word1, word2, dataloader_row):
        valid_images = [img for img in dataloader_row['images'] if img is not None]
        output_embeddings = []
        for image1, image2 in itertools.combinations(valid_images, 2):
            curr_image_embeddings = self.image_embeddings([image1, image2])
            curr_text_embeddings = self.text_embeddings([word1, word2])
            output_embeddings.append({
                'image_embeddings': curr_image_embeddings,
                'text_embeddings': curr_text_embeddings,
                'multimodal_embeddings': self.multimodal_embeddings(curr_image_embeddings, curr_text_embeddings)
            })
        return output_embeddings
    
    def compute_tsne_visualization(self):
        # Initialize collections
        label_to_embeddings = {}
        word_graph = nx.Graph()
        # Process data
        for d in tqdm(self.dataloader, desc=f"Creating {self.name} tSNE visualization"):
            for (text1, text2) in itertools.combinations(d['text'], 2):
                curr_embeddings = self.embeddings(text1, text2, d)
                # Store embeddings for each text
                for text, embedding in zip([text1, text2], curr_embeddings[0]['text_embeddings']):
                    if text not in label_to_embeddings:
                        label_to_embeddings[text] = embedding
                # Add words to the graph, creating edges between them
                word_graph.add_edge(text1, text2)
        
        # Extract the embeddings and labels from the dictionary
        labels = list(label_to_embeddings.keys())
        embeddings = np.array([label_to_embeddings[label].cpu().numpy().flatten() for label in labels])
        
        # Apply t-SNE
        tsne = TSNE(n_components=2, random_state=42, perplexity=10)
        transformed = tsne.fit_transform(embeddings)
        
        # Find connected components (groups of words sharing common relations)
        components = list(nx.connected_components(word_graph))
        # Assign a unique color for each connected component
        component_colors = {frozenset(component): color for component, color in 
                            zip(components, sns.color_palette("husl", len(components)))}
        
        # Assign color to points based on the connected component
        word_to_color = {}  # Store color mapping for words
        for component, color in component_colors.items():
            for word in component:
                word_to_color[word] = color
        
        # Plot the t-SNE output
        plt.figure(figsize=(10, 8))
        
        # Create a dictionary to store component labels for the legend
        component_to_label = {}
        legend_handles = []
        
        # Plot each point with its respective color
        for i, label in enumerate(labels):
            embedding = transformed[i]
            color = word_to_color.get(label, 'gray')  # Default to 'gray' if no color found
            
            # Find which component this word belongs to for legend grouping
            for comp in components:
                if label in comp:
                    comp_key = frozenset(comp)
                    if comp_key not in component_to_label:
                        component_to_label[comp_key] = f"Group {len(component_to_label) + 1}"
                        # Add to legend only once per component
                        legend_handle = plt.scatter(embedding[0], embedding[1], color=color, 
                                                alpha=0.7, s=80, label=component_to_label[comp_key])
                        legend_handles.append(legend_handle)
                    else:
                        plt.scatter(embedding[0], embedding[1], color=color, alpha=0.7, s=80)
                    break
            else:
                # If word isn't in any component
                plt.scatter(embedding[0], embedding[1], color='gray', alpha=0.7, s=80)
                
            plt.annotate(label, (embedding[0], embedding[1]), textcoords="offset points", 
                        xytext=(0, 10), ha='center', fontsize=12)
        
        plt.title(f"t-SNE Visualization of Word Embeddings for {self.name.upper()}")
        
        # Add legend if we have groups
        if legend_handles:
            plt.legend(handles=legend_handles, loc="best", bbox_to_anchor=(1, 1))
        
        # Save first, then show
        plt.savefig('tsne_visualization.png', bbox_inches='tight')
        plt.show()
        
    def normalize_embeddings(self, embeddings):
        """Normalize embeddings to unit L2 norm"""
        return [embedding / embedding.norm(dim=-1, keepdim=True) for embedding in embeddings]
    
