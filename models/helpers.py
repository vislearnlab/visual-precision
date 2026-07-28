from pathlib import Path
from vislearnlabpy.embeddings.generate_embeddings import EmbeddingGenerator

# ── Helpers ───────────────────────────────────────────────────────────────────

def _image_doc(output_path: str, model_type: str) -> str:
    return str(Path(output_path) / "image_embeddings" / f"{model_type}_image_embeddings_doc.docs")


def _text_doc(output_path: str, model_type: str) -> str:
    return str(Path(output_path) / "text_embeddings" / f"{model_type}_text_embeddings_doc.docs")


def _load_or_generate(gen: EmbeddingGenerator, output_path: str, model_type: str, input_csv: str, input_dir: str) -> None:
    """Generate embeddings only if the image store doesn't already exist."""
    doc = _image_doc(output_path, model_type)
    if Path(doc + ".bin").exists() or Path(doc).exists():
        print(f"    (using cached embeddings at {doc})")
        return
    gen.generate_image_embeddings(
        output_path=output_path,
        input_csv=input_csv,
        input_dir=input_dir,
        id_column=None,
        batch_size=32,
    )
