# Models

Computes similarity scores for every image pair in
`data/metadata/level-imagepair_data.csv` and writes them to `data/embeddings/`.

Everything runs through `generate_similarities.py`. Run it from this directory.

## Install

```bash
cd models
pip install -r ../requirements.txt -r requirements.txt
```

Copy `.env_template` to `.env` in the repo root and set `PROJECT_PATH`.
For `dinov3` you also need `HF_TOKEN`, and you have to accept the license on
HuggingFace first.

## Run

```bash
python generate_similarities.py --device mps
```

Use `--device cpu` or `--device cuda:0` if you're not on a Mac.
`--help` lists the rest of the options.

`clip` and `cvcl` need the extra setup below. To skip them:

```bash
python generate_similarities.py --models clip-hf dinov2 dinov3 --device mps
```

## Setup: clip

```bash
pip uninstall -y clip
pip install git+https://github.com/openai/CLIP.git
```

The uninstall matters. A different package on PyPI is also called `clip`.

## Setup: cvcl

CVCL isn't on PyPI, so you copy the code in by hand.

**1. Get the code.** Clone it outside this project, then move the inner
`multimodal` folder in:

```bash
git clone https://github.com/wkvong/multimodal-baby.git ~/code/multimodal-baby
mv ~/code/multimodal-baby/multimodal <repo>/models/multimodal
```

Move the inner folder, not the whole repo. `models/multimodal/multimodal_lit.py`
should exist when you're done. It's already gitignored.

**2. Install its deps.**

```bash
pip install spacy pytorch-lightning pycocoevalcap
python -m spacy download en_core_web_sm
```

**3. Check it.**

```bash
python -c "import generate_similarities; print('ok')"
```

Never run `pip install multimodal`. That's an unrelated project and it breaks the
whole script, not just CVCL.

The weights download on first use.

## If something breaks

| Error | Fix |
|---|---|
| `module 'clip' has no attribute 'load'` | Redo the `clip` setup. |
| `ModuleNotFoundError: torchmetrics` from a `vqa.py` file | Wrong `multimodal`. `pip uninstall multimodal`, then redo the `cvcl` setup. |
| `Can't find model 'en_core_web_sm'` | Run the `spacy download` line. |
| `401` / `403` on `dinov3` | Accept the license on HuggingFace, set `HF_TOKEN` in `.env`. |
| `ModuleNotFoundError` for `helpers`, `cvcl_model`, `openclip_sweep` | You're not in `models/`. |

## Good to know

- Embeddings cache in `models/output/`. Later runs reuse them. Delete a model's
  folder to recompute.
- With no `--models`, the script also runs a 13-layer analysis of `clip-hf`, which
  is slow.
- `--openclip-checkpoints` pulls 40 large checkpoints. Leave it off unless you need it.
- `--output-dir` only moves the cached embeddings. Result CSVs always go to
  `data/embeddings/`, whatever the script prints at the end.
