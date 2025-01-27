import torch
import clip
from PIL import Image
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from torch.nn.functional import cosine_similarity
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
project_dir = os.environ.get("PROJECT_PATH")
images_path = os.path.join(project_dir, 'stimuli', 'lookit', 'exp1', 'img')
metadata_path = os.path.join(project_dir, 'data', 'metadata')

# Load and preprocess images
def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    return preprocess(image).unsqueeze(0).to(device)

def preprocess_text(text):
    return torch.cat([clip.tokenize(f"a photo of a {text}")]).to(device)

def similarities(word1, word2):
    image1 = os.path.join(images_path, word1 + '.jpg')
    image2 = os.path.join(images_path, word2 + '.jpg')
    if not os.path.isfile(image1) or not os.path.isfile(image2):
        print(f"One or both image files do not exist for {word1} and {word2}")
        return None
    curr_image_embeddings = image_embeddings([image1, image2])
    curr_text_embeddings = text_embeddings([word1, word2])
    curr_multimodal_embeddings = [(a + b) / 2 for a, b in zip(curr_image_embeddings, curr_text_embeddings)]
    similarity_scores = {
        'image_similarity': similarity(curr_image_embeddings[0], curr_image_embeddings[1]),
        'text_similarity': similarity(curr_text_embeddings[0], curr_text_embeddings[1]),
        'multimodal_similarity': similarity(curr_multimodal_embeddings[0], curr_multimodal_embeddings[1])
    }
    print(f"{word1} and {word2} similarity scores: {similarity_scores}")
    return similarity_scores

def similarity(embeddings1, embeddings2):
    # Compute cosine similarity
    similarity_score = cosine_similarity(embeddings1, embeddings2)
    return similarity_score.item()

def text_embeddings(words):
    all_text_features = [preprocess_text(word) for word in words]
    with torch.no_grad():
        embeddings = [model.encode_text(text_features) for text_features in all_text_features]
    return normalize_embeddings(embeddings)

def image_embeddings(image_paths):
    # Load and preprocess images
    images = [preprocess_image(image_path) for image_path in image_paths]

    # Extract embeddings
    with torch.no_grad():
        embeddings = [model.encode_image(image) for image in images]
    return normalize_embeddings(embeddings)

# Normalize each embedding to have a unit L2 norm
def normalize_embeddings(embeddings):
    return [embedding / embedding.norm(dim=-1, keepdim=True) for embedding in embeddings]

def lookit_similarities():
    trial_info_df = pd.read_csv(os.path.join(metadata_path, 'lookit_trial_timing_info.csv'))
    left_words = trial_info_df['Trials.leftImage'].tolist()
    right_words = trial_info_df['Trials.rightImage'].tolist()
    # Collect all unique words
    words = list(set(left_words + right_words))
    # Initialize a DataFrame for similarities
    similarity_df = pd.DataFrame(index=words, columns=words)
    similarity_data = []
    word_pair_set = set()
    # Populate the similarity DataFrame
    for word1, word2 in zip(left_words, right_words):
        pair = tuple(sorted([word1, word2]))  # Ensure consistent ordering (word1, word2)
        if pair not in word_pair_set:
            curr_similarities = similarities(word1, word2)
            if curr_similarities: 
                similarity_data.append({
                'word1': word1, 'word2': word2,
                **curr_similarities  # Flatten the dictionary directly into columns
                })
                word_pair_set.add(pair)
    # Create and save DataFrame
    similarity_df = pd.DataFrame(similarity_data)
    similarity_df.to_csv(os.path.join(metadata_path, 'similarities.csv'), index=False)
    return similarity_df
