import os
import pandas as pd
import re
from dotenv import load_dotenv
from PIL import Image
from torch.utils.data import Dataset, DataLoader

load_dotenv()
project_dir = os.environ.get("PROJECT_PATH")

class StimuliDataset(Dataset):
  def __init__(self, dataset_file, images_folder=None):
    self.manifest = pd.read_csv(dataset_file)
    self.images_folder = images_folder
    self.num_text_cols = sum(1 for c in self.manifest.columns if re.compile("text[0-9]").match(c))
    self.num_image_cols = len([c for c in self.manifest.columns if re.compile("image[0-9]").match(c)])

  def __len__(self):
     return len(self.manifest)

  def __getitem__(self, idx):
    row = self.manifest.iloc[idx]
    texts = [row[f"text{i}"] for i in range(1, self.num_text_cols + 1)]
    images = []
    image_paths = self._get_image_paths(row)
    for image_path in image_paths:
      if image_path is None:
        images.append(None)
      else:
        with Image.open(image_path).convert('RGB') as img:
          images.append(img.copy())  # Copy the image data to memory
    return {"images": images, "text": texts}

  def _get_image_paths(self, row):
    # If this is a text only dataset
    if self.images_folder is None:
      return [None] * self.num_text_cols
    # If images are not in the manifest
    elif self.num_image_cols == 0:
      return [os.path.join(self.images_folder, row[f"text{i}"] + ".jpg") for i in range(1, self.num_text_cols + 1)]
    else:
      return [os.path.join(self.images_folder, row[f"image{i}"]) for i in range(1, self.num_image_cols + 1)]

class StimuliLoader():
  def __init__(self, dataset_file, batch_size=1, image_folder=None, stimuli_type='lookit'):
    self.stimuli_type = stimuli_type
    self.image_folder = image_folder
    self.batch_size = batch_size
    self.dataset_file = dataset_file
  
  def collator(self, batch):
    return {key: [item for ex in batch for item in ex[key]] for key in batch[0]}
     
  def dataloader(self):
    dataset = StimuliDataset(self.dataset_file, self.image_folder)
    return DataLoader(dataset, batch_size=self.batch_size, collate_fn=self.collator)
# TODO: allow for calculating all possible pairwise similarities in a space to do RSA etc.
