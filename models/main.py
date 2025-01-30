from clip_model import CLIPGenerator
from cvcl_model import CVCLGenerator
from openclip_model import OpenCLIPGenerator
import open_clip
import os

# Generate similarity scores for CLIP, CVCL and OpenCLIP models
def load_clip():
    CLIPGenerator().lookit_similarities()

def load_cvcl():
    CVCLGenerator().lookit_similarities()

def load_openclip():
    epochs = sorted(os.listdir('openclip/checkpoints'), key=lambda x: int(x.split('_')[1].split('.')[0]))
    for i, epoch in enumerate(epochs):
        print(f'Processing epoch {epoch}')
        model, _, preprocess = open_clip.create_model_and_transforms('ViT-H-14', pretrained=f'openclip/checkpoints/{epoch}', load_weights_only=False) 
        OpenCLIPGenerator(model, preprocess, epoch=i+1).lookit_similarities()

load_clip()
load_cvcl()
load_openclip()
