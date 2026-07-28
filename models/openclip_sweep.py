import numpy as np
from vislearnlabpy.embeddings.embedding_store import EmbeddingStore
from vislearnlabpy.embeddings.generate_embeddings import EmbeddingConfig, EmbeddingGenerator
import os
import requests
import pandas as pd
from tqdm import tqdm
from helpers import _text_doc, _image_doc, _load_or_generate
# OpenCLIP checkpoint sweep: log-spaced training checkpoints of one architecture,
# downloaded from a HF "all-checkpoints" dataset repo (requires the optional open_clip
# package). Long-format output since each checkpoint is a snapshot of the same model,
# not a different model. Opt-in via --openclip-checkpoints (each checkpoint is a large
# download).
OPENCLIP_CHECKPOINT_REPO = "laion/CLIP-ViT-H-14-laion2B-s32B-b79K-all-checkpoints"
OPENCLIP_CHECKPOINT_MODEL_NAME = "ViT-H-14"
OPENCLIP_TOTAL_CHECKPOINTS = 256
OPENCLIP_NUM_SELECTIONS = 40

# ── OpenCLIP checkpoint sweep ─────────────────────────────────────────────────

def _select_checkpoint_epochs(total_checkpoints: int, num_selections: int) -> list:
    """Logarithmically-spaced epoch numbers in [1, total_checkpoints], deduplicated."""
    log_scale = np.logspace(np.log2(1), np.log2(total_checkpoints), base=2, num=num_selections)
    return sorted(set(np.round(log_scale).astype(int).tolist()))


def _download_openclip_checkpoint(epoch: int, checkpoint_dir: str, repo: str) -> str:
    """Download one training-epoch checkpoint from a HF dataset repo (cached if present).

    Streams to a .part file and renames on completion, so an interrupted download can
    never be mistaken for a valid cached checkpoint on the next run.
    """
    os.makedirs(checkpoint_dir, exist_ok=True)
    output_path = os.path.join(checkpoint_dir, f"epoch_{epoch}.pt")
    if os.path.exists(output_path):
        print(f"    (using cached checkpoint at {output_path})")
        return output_path
    url = f"https://huggingface.co/datasets/{repo}/resolve/main/epoch_{epoch}.pt"
    tmp_path = output_path + ".part"
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        with open(tmp_path, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc=f"    epoch_{epoch}.pt"
        ) as pbar:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                pbar.update(len(chunk))
    os.replace(tmp_path, output_path)
    return output_path


def openclip_checkpoint_df(epoch: int, checkpoint_path: str, text_pairs, output_dir: str, device: str, input_csv: str, input_dir: str) -> pd.DataFrame:
    """Return a long DataFrame (text1, text2, epoch, similarities) for one checkpoint."""
    model_type = f"openclip_epoch{epoch}"
    output_path = os.path.join(output_dir, "openclip_checkpoints", f"epoch{epoch}")

    gen = EmbeddingGenerator(config=EmbeddingConfig(
        model_type=model_type,
        model_source="openclip",
        model_name=OPENCLIP_CHECKPOINT_MODEL_NAME,
        checkpoint_path=checkpoint_path,
        epoch=epoch,
        output_type="doc",
        device=device,
    ))
    _load_or_generate(gen, output_path, model_type, input_csv, input_dir)

    image_store = EmbeddingStore.from_doc(_image_doc(output_path, model_type))
    text_store = EmbeddingStore.from_doc(_text_doc(output_path, model_type))

    image_df = image_store.retrieve_similarities(text_pairs=text_pairs)
    image_df = image_df.rename(columns={"cosine_similarity": "image_similarity"})
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

    df.insert(2, "epoch", epoch)
    return df


def openclip_checkpoint_sweep_df(text_pairs, output_dir: str, device: str, input_csv: str, input_dir: str) -> pd.DataFrame:
    """Download and compute similarities for each selected training checkpoint."""
    epochs = _select_checkpoint_epochs(OPENCLIP_TOTAL_CHECKPOINTS, OPENCLIP_NUM_SELECTIONS)
    checkpoint_dir = os.path.join(output_dir, "openclip_checkpoints")
    epoch_dfs = []
    for epoch in epochs:
        print(f"  epoch {epoch}…")
        checkpoint_path = _download_openclip_checkpoint(epoch, checkpoint_dir, OPENCLIP_CHECKPOINT_REPO)
        epoch_dfs.append(openclip_checkpoint_df(epoch, checkpoint_path, text_pairs, output_dir, device, input_csv, input_dir))
    return pd.concat(epoch_dfs, ignore_index=True)
