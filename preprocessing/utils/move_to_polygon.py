from tqdm import tqdm
from glob import glob
import shutil
import os

polygon_folder = "/Volumes/vislearnlab/experiments/visvocab/data/raw/original_videos/webm"
downloads_folder = "/Users/visuallearninglab/Downloads"
for file in tqdm(glob(downloads_folder + "/*.webm")):
    filename = os.path.basename(file)
    dest_path = os.path.join(polygon_folder, filename)

    if not os.path.exists(dest_path):
        shutil.move(file, dest_path)
    else:
        print(f"Skipped (already exists): {filename}")
