import os
import re
import pandas as pd

from PIL import Image
from dotenv import load_dotenv

load_dotenv()
project_dir = os.environ.get("PROJECT_PATH")

class StimuliLoader():
    """
    Dataset from a given dataset folder.
    TODO: convert to DataSet class
    """
    def __init__(self, stimuli_type='lookit'):
      self.stimuli_type = stimuli_type
      self.images_path = os.path.join(project_dir, 'stimuli', 'lookit', 'exp1', 'img')
      self.metadata_path = os.path.join(project_dir, 'data', 'metadata')
    
    def word_to_image(self, word):
      image_path = os.path.join(self.images_path, word + '.jpg')
      if not os.path.isfile(image_path):
        print(f"Image file does not exist for {word}")
        return None
      return image_path

    def words(self):
      trial_info_df = pd.read_csv(os.path.join(self.metadata_path, 'stimuli_all.csv'))
      left_words = trial_info_df['Word1'].tolist()
      right_words = trial_info_df['Word2'].tolist()
      return left_words, right_words

    def save_df(self, df, filename):
      filepath = os.path.join(self.metadata_path, filename)
      if os.path.exists(filepath):
      # Read existing CSV and append new data if it belongs to a different epoch
      # TODO: change epoch to be a more variable field, add logging if dataframe is not being updated
        existing_df = pd.read_csv(filepath)
        if 'epoch' in existing_df.columns and 'epoch' in df.columns:
            if not any(existing_df['epoch'].isin(df['epoch'])):
                combined_df = pd.concat([existing_df, df], ignore_index=True)
            else:
                combined_df = existing_df
                print(f"Dataframe {filename} exists, not updating")
        else:
            combined_df = existing_df
            print(f"Dataframe {filename} exists, not updating")
        combined_df.to_csv(filepath, index=False)
      else:
        df.to_csv(filepath, index=False)
