import requests
import numpy as np
import os

# Total checkpoints and the number of selections you want, we use 40 selections here to generate 32 unique checkpoints 
total_checkpoints = 256
num_selections = 40

def download_checkpoint(checkpoint):
    url = f"https://huggingface.co/datasets/laion/CLIP-ViT-H-14-laion2B-s32B-b79K-all-checkpoints/resolve/main/epoch_{checkpoint}.pt"
    output_path = f"checkpoints/epoch_{checkpoint}.pt"
    if os.path.exists(output_path):
        print(f"File already exists at {output_path}")
        return
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"File downloaded successfully and saved to {output_path}")
    else:
        print(f"Failed to download file. HTTP Status: {response.status_code}")

def download_all_checkpoints():
    # Generate the logarithmically spaced checkpoints
    log_scale_checkpoints = np.logspace(np.log2(1), np.log2(total_checkpoints), base=2, num=num_selections)

    # Convert to integers and remove duplicates
    log_scale_checkpoints = np.round(log_scale_checkpoints).astype(int)

    # Remove duplicates by converting to a set and back to an array
    unique_checkpoints = np.unique(log_scale_checkpoints)

    for checkpoint in unique_checkpoints:
        download_checkpoint(checkpoint)

download_all_checkpoints()