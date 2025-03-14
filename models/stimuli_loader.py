import os
import pandas as pd
import re
from dotenv import load_dotenv
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import random

random.seed(2)

load_dotenv()
project_dir = os.environ.get("PROJECT_PATH")

class StimuliDataset(Dataset):
  def __init__(self, dataset_file, images_folder=None, id_column=None):
    self.manifest = pd.read_csv(dataset_file)
    self.images_folder = images_folder
    self.num_text_cols = sum(1 for c in self.manifest.columns if re.compile("text[0-9]").match(c))
    self.num_image_cols = len([c for c in self.manifest.columns if re.compile("image[0-9]").match(c)])
    self.id_column = id_column

  def __len__(self):
     return len(self.manifest)

  def __getitem__(self, idx):
    row = self.manifest.iloc[idx]
    texts = [str(row[f"text{i}"]) for i in range(1, self.num_text_cols + 1)]
    images = []
    image_paths = self._get_image_paths(row)
    for image_path in image_paths:
      if image_path is None or not os.path.exists(image_path):
        images.append(None)
      else:
        with Image.open(image_path).convert('RGB') as img:
          images.append(img.copy())  # Copy the image data to memory
    return {"images": images, "text": texts, "id": [row[self.id_column] if self.id_column is not None else random.randint(0, 1000000)]}

  def _get_image_paths(self, row):
    # If this is a text only dataset
    if self.images_folder is None:
      return [None] * self.num_text_cols
    # If images are not in the manifest
    elif self.num_image_cols == 0:
      return [os.path.join(self.images_folder, row[f"text{i}"] + ".jpg") for i in range(1, self.num_text_cols + 1)]
    else:
      # allowing for a secondary image path to be provided with different images in the same stimuli sets stored in different subpaths
      return [
    os.path.join(self.images_folder, *(row["image_path"],) if "image_path" in row else (), row[f"image{i}"])
    for i in range(1, self.num_image_cols + 1)]

class StimuliLoader():
  def __init__(self, dataset_file, batch_size=1, image_folder=None, id_column=None, stimuli_type='lookit', pairwise=False):
    self.stimuli_type = stimuli_type
    self.image_folder = image_folder
    self.batch_size = batch_size
    self.dataset_file = dataset_file
    self.id_column = id_column
    self.pairwise = pairwise
  
  def collator(self, batch):
    return {key: [item for ex in batch for item in ex[key]] for key in batch[0]}
     
  def dataloader(self):
    dataset = StimuliDataset(self.dataset_file, self.image_folder, self.id_column)
    return DataLoader(dataset, batch_size=self.batch_size, collate_fn=self.collator)
# TODO: allow for calculating all possible pairwise similarities in a space to do RSA etc.
