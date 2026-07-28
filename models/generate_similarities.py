"""
Visual precision similarity script.

For each model in MODELS, generates image embeddings (and text embeddings for
multimodal models), then computes cosine similarities for every word pair
listed in INPUT_CSV.

Outputs
-------
data/embeddings/similarities-all_data.csv
    Wide CSV — one row per (text1, text2) pair, one column per
    (model, similarity_type).  Similarity types: ``image_similarity`` for all
    models; additionally ``text_similarity`` and ``multimodal_similarity``
    (cross-modal: cosine(image[text1], text[text2])) for multimodal models.

data/embeddings/similarities-layerwise_data.csv  (separate)
    Same format but one column per layer of LAYERWISE_MODEL.

data/embeddings/similarities-openclip_data.csv  (separate, opt-in via --openclip-checkpoints)
    Long CSV — one row per (word pair, checkpoint epoch): columns word1, word2,
    epoch, image_similarity, text_similarity, multimodal_similarity. Covers
    OPENCLIP_NUM_SELECTIONS log-spaced training checkpoints of one OpenCLIP
    architecture (OPENCLIP_CHECKPOINT_MODEL_NAME), downloaded from
    OPENCLIP_CHECKPOINT_REPO. Off by default since each checkpoint is a large
    download.

output/<model_name>/image_embeddings/*.docs
output/<model_name>/text_embeddings/*.docs  (multimodal models only)
    Embedding stores — reloaded on subsequent runs so embeddings are not
    regenerated if the .docs file already exists.

Usage
-----
    VISUAL_PRECISION_PATH=/path/to/dataset python generate_embeddings.py

    python generate_embeddings.py --models clip dinov2 --device cuda:0 \
        --input-csv path/to/pairs.csv --input-dir path/to/images --output-dir output

Run with --help to see all options. --models filters MODELS/LAYERWISE_MODEL down to the
given names; omit it to run everything. The OpenCLIP checkpoint sweep is separate from
--models since it isn't a named preset -- pass --openclip-checkpoints to enable it.
"""

import argparse
import os
from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm

from vislearnlabpy.embeddings.embedding_store import EmbeddingStore
from vislearnlabpy.embeddings.generate_embeddings import EmbeddingGenerator
from vislearnlabpy.embeddings.similarity_utils import combine_sim_dfs, csv_to_text_pairs
from vislearnlabpy.models.hf_model import MODEL_PRESETS
from openclip_sweep import OPENCLIP_NUM_SELECTIONS, OPENCLIP_CHECKPOINT_REPO, openclip_checkpoint_sweep_df
from cvcl_model import cvcl_embedding_generator
from helpers import _load_or_generate, _image_doc, _text_doc
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()
PROJECT_PATH = os.environ.get("PROJECT_PATH", "/Users/vislearnlab/Documents/visual-precision")
INPUT_CSV = os.path.join(PROJECT_PATH, "data", "metadata", "level-imagepair_data.csv")
INPUT_DIR = os.path.join(PROJECT_PATH, "stimuli", "lookit", "exp1", "img")
OUTPUT_DIR = "output"
OUTPUT_CSV_DIR = os.path.join(PROJECT_PATH, "data", "embeddings")
DEVICE = os.environ.get("DEVICE", "cpu")

# Models included in the combined CSV (any key from MODEL_PRESETS works here, plus
# "cvcl" which is handled separately in model_sim_df since it isn't a MODEL_PRESETS entry)
MODELS = [
    "clip",
    "clip-hf",
    "cvcl",
    "dinov2",
    "dino_say_vitb14",
    "dino_imagenet100_vitb14",
    "dinov3-babyview",
    "dinov3",
]

# Layer-wise analysis: any MODEL_PRESETS key that has num_layers defined.
# Indices: 0 = patch-embedding output, 1..N = transformer blocks.
LAYERWISE_MODEL = "clip-hf"
LAYERWISE_LAYERS = list(range(MODEL_PRESETS[LAYERWISE_MODEL]["num_layers"]))


# ── Per-model similarity ──────────────────────────────────────────────────────

def model_sim_df(model_name: str, text_pairs) -> pd.DataFrame:
    """Return a DataFrame with image (and text) similarities for one model."""
    output_path = os.path.join(OUTPUT_DIR, model_name)

    if model_name == "cvcl":
        model_type = "cvcl"
        gen = cvcl_embedding_generator(device=DEVICE)
    else:
        preset = MODEL_PRESETS[model_name]
        model_type = preset["model_type"]
        gen = EmbeddingGenerator.from_model(model_name, output_type="doc", device=DEVICE)

    _load_or_generate(gen, output_path, model_type, INPUT_CSV, INPUT_DIR)

    image_store = EmbeddingStore.from_doc(_image_doc(output_path, model_type))
    image_df = image_store.retrieve_similarities(text_pairs=text_pairs)
    image_df = image_df.rename(columns={"cosine_similarity": "image_similarity"})

    # Multimodal models also produce text embeddings
    text_doc_path = _text_doc(output_path, model_type)
    if Path(text_doc_path + ".bin").exists() or Path(text_doc_path).exists():
        text_store = EmbeddingStore.from_doc(text_doc_path)
        text_df = text_store.retrieve_similarities(text_pairs=text_pairs)
        text_df = text_df.rename(columns={"cosine_similarity": "text_similarity"})
        df = image_df.merge(text_df, on=["text1", "text2"], how="left")

        # Cross-modal (multimodal) similarity: Luce choice rule P(image[text1] | text[text1])
        multimodal_df = image_store.multimodal_prob(text_store, text_pairs, rule="luce")
        multimodal_df['multimodal_similarity'] = 1 - multimodal_df['multimodal_prob']
        multimodal_df = multimodal_df.rename(
            columns={"id2": "text2"}
        ).drop(columns=["id1", "multimodal_prob"])
        df = df.merge(multimodal_df, on=["text1", "text2"], how="left")
    else:
        df = image_df

    return df

# ── Layer-wise similarity ─────────────────────────────────────────────────────

def layerwise_sim_df(model_name: str, layers, text_pairs) -> pd.DataFrame:
    """Return a wide DataFrame with one image-similarity column per layer."""
    layer_dfs = {}
    for layer in layers:
        print(f"    layer {layer}…")
        output_path = os.path.join(OUTPUT_DIR, "layerwise", f"layer{layer}")
        gen = EmbeddingGenerator.from_model(model_name, layer=layer, output_type="doc", device=DEVICE)
        model_type = gen.model_type  # auto-suffixed by from_model, e.g. "clip_layer5"
        _load_or_generate(gen, output_path, model_type, INPUT_CSV, INPUT_DIR)
        store = EmbeddingStore.from_doc(_image_doc(output_path, model_type))
        df = store.retrieve_similarities(text_pairs=text_pairs)
        df = df.rename(columns={"cosine_similarity": "image_similarity"})
        layer_dfs[f"layer{layer}"] = df
    return combine_sim_dfs(layer_dfs)

# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", default=None,
                        help="Only (re)generate these model names, filtering MODELS and "
                             "LAYERWISE_MODEL (a name not present in either is simply ignored). "
                             "Default: run all of them.")
    parser.add_argument("--device", default=DEVICE,
                        help="Device to run models on, e.g. 'cpu' or 'cuda:0'. Default: $DEVICE env var or 'cpu'.")
    parser.add_argument("--input-csv", default=INPUT_CSV, help="Path to the word-pair metadata CSV.")
    parser.add_argument("--input-dir", default=INPUT_DIR, help="Directory containing stimulus images.")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Directory to write embeddings and output CSVs to.")
    parser.add_argument("--openclip-checkpoints", action="store_true",
                        help=f"Also run the OpenCLIP checkpoint sweep ({OPENCLIP_NUM_SELECTIONS} "
                             f"checkpoints from {OPENCLIP_CHECKPOINT_REPO}). Off by default -- "
                             "each checkpoint is a large download.")
    return parser.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = _parse_args()
    DEVICE = args.device
    INPUT_CSV = args.input_csv
    INPUT_DIR = args.input_dir
    OUTPUT_DIR = args.output_dir

    models_to_run = MODELS if args.models is None else [m for m in MODELS if m in args.models]
    run_layerwise = args.models is None or LAYERWISE_MODEL in args.models

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    text_pairs = csv_to_text_pairs(INPUT_CSV)
    # Include both orderings so multimodal_similarity (Luce, asymmetric) is computed
    # with each of text1/text2 as the target.
    text_pairs = text_pairs + [(text2, text1) for text1, text2 in text_pairs]

    # ── Combined CSV (all standard models) ───────────────────────────────────
    if models_to_run:
        print("Generating combined similarities…")
        model_dfs = {}
        for model_name in models_to_run:
            print(f"  {model_name}…")
            model_dfs[model_name] = model_sim_df(model_name, text_pairs)

        combined = combine_sim_dfs(model_dfs, output_csv=os.path.join(OUTPUT_CSV_DIR, "similarities-all_data.csv"))
        print(f"  → {OUTPUT_DIR}/similarities-all_data.csv  ({len(combined)} rows, {len(combined.columns)} cols)")
    else:
        print("Skipping combined similarities (no MODELS selected)")

    # ── OpenCLIP checkpoint sweep (separate, opt-in) ─────────────────────────
    if args.openclip_checkpoints:
        print("\nGenerating OpenCLIP checkpoint-sweep similarities…")
        ocs_df = openclip_checkpoint_sweep_df(text_pairs, OUTPUT_DIR, DEVICE, INPUT_CSV, INPUT_DIR)
        ocs_path = os.path.join(OUTPUT_CSV_DIR, "similarities-openclip_data.csv")
        ocs_df.to_csv(ocs_path, index=False)
        print(f"  → {ocs_path}  ({len(ocs_df)} rows, {len(ocs_df.columns)} cols)")
    else:
        print("\nSkipping OpenCLIP checkpoint sweep (pass --openclip-checkpoints to enable)")

    # ── Layer-wise CSV (separate) ─────────────────────────────────────────────
    if run_layerwise:
        print(f"\nGenerating layer-wise similarities for {LAYERWISE_MODEL}…")
        lw = layerwise_sim_df(LAYERWISE_MODEL, LAYERWISE_LAYERS, text_pairs)
        lw_path = os.path.join(OUTPUT_CSV_DIR, "similarities-layerwise_data.csv")
        lw.to_csv(lw_path, index=False)
        print(f"  → {lw_path}  ({len(lw)} rows, {len(lw.columns)} cols)")
    else:
        print(f"\nSkipping layer-wise similarities ({LAYERWISE_MODEL} not in --models)")
