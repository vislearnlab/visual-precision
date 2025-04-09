from clip_model import CLIPGenerator
from cvcl_model import CVCLGenerator
from openclip_model import OpenCLIPGenerator
from saycamvit_model import SayCamVIT
from imagenetvit_model import ImageNetVIT
import torch
import open_clip
import os

# Generate similarity scores for CLIP, CVCL and OpenCLIP models
def load_contrastives():
    CLIPGenerator().lookit_similarities()
    CVCLGenerator().lookit_similarities()

def load_vits():
    SayCamVIT().lookit_similarities()
    ImageNetVIT().lookit_similarities()

def load_openclip():
    epochs = sorted(os.listdir('openclip/checkpoints'), key=lambda x: int(x.split('_')[1].split('.')[0]))
    for i, epoch in enumerate(epochs):
        print(f'Processing epoch {epoch}')
        model, _, preprocess = open_clip.create_model_and_transforms('ViT-H-14', pretrained=f'openclip/checkpoints/{epoch}', load_weights_only=False) 
        OpenCLIPGenerator(model, preprocess, epoch=i+1).lookit_similarities()

# Working with CPU capacity
torch.set_num_threads(1)
load_contrastives()
load_openclip()
load_vits()
#CLIPGenerator(device="cuda:0").compute_tsne_visualization()
#CLIPGenerator(device="cuda:0").lookit_similarities()
