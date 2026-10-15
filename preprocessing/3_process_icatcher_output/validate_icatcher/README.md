# Validate iCatcher+ (manual annotation game)

Human gaze coding for a ~20% sample of videos, used as ground truth to validate the
iCatcher+ output. Annotators code every frame `left` / `right` / `away`.

> [WARNING]
> **NEVER touch `select_validation_videos.py`.** The validation sample is already drawn, committed and
> partly annotated. Do not run it, re-seed it, or edit its arguments or paths. Re-running it overwrites
>
> **Please talk to the team first and expect to discard the annotations collected so far.**

## Quick Start

1. `cd preprocessing/3_process_icatcher_output/validate_icatcher`
2. `conda activate visualprecision`
3. Mount the Polygon volume and set `SERVER_PATH` in the repo-root `.env` (see [Where the data comes from](#where-the-data-comes-from))
4. `python annotate_videos.py`
5. Open <http://localhost:8765>
6. Enter your username and start labeling. Keys are listed at the bottom of the page.

---

## Where the data comes from

The videos and the iCatcher csv are always read from the **mounted Polygon volume**: connect to the
VPN, mount the share, set `SERVER_PATH` in the repo-root `.env`, and run on your own machine. Both
scripts resolve everything from that one root:

```python
ROOT = Path(os.environ['SERVER_PATH'])  # the mounted Polygon volume

SHARED = ROOT / 'preprocessing' / '3_process_icatcher_output' / 'validate_icatcher'
```

`SHARED` is where `video_claims.csv` and `.annotate.lock` live. Because each annotator has their own
checkout it points at the `validate_icatcher` directory **on the volume**, not at the local one, so
everyone claims against the same file. See [Concurrency](#concurrency).

The claims file on the volume is the live one; the copy committed in git is stale and gitignored.

## Requirements

- `pandas` and `python-dotenv`
- `ffmpeg` on `PATH`, or `pip install imageio-ffmpeg`
- `SERVER_PATH` set in the repo-root `.env`, pointing at the mounted Polygon volume

## How work is handed out

Annotators are identified by the username typed on the login screen,

Videos are claimed **a participant at a time**: when you need new work the tool claims every selected
video of the next unclaimed participant, and you work through all ~32 of them in a row before moving
on. Claims are recorded in `video_claims.csv` and claimed videos are never offered to anyone else.

`video_claims.csv` is gitignored. It is per-deployment state, not repo content. The live one lives on
the volume (polygon) you are running against, so **don't delete it**.

## Concurrency

The `flock` is taken on `.annotate.lock` on the volume, so simultaneous annotators serialise their
writes. This holds **only** because `SHARED` is on the volume — pointing it at the local checkout
would have each machine locking its own file while writing the same csv on the share.

## How the selection was made

`select_validation_videos.py` picks ~20% of all videos by choosing whole random participants with the minimum amout of valid videos.

The committed result is 1492 videos (19.9%) from 47 participants at `--seed 42`;
`validation_selection.txt` is the human-readable record.

**Do not re-run it -> see the warning at the top of this file.**

## Troubleshooting

**Port already in use / stale UI.** `annotate_videos.py` scans ports 8765–8814 and prints the one it
got. A leftover process still holding 8765 means the new instance lands on 8766 while your browser
still points at 8765 — you would be annotating against the old process. Check with
`lsof -nP -iTCP:8765 -sTCP:LISTEN` and kill the stale pid before starting.

**`FileNotFoundError` on `level-looks_source-icatcher_data.csv`.** The volume is not mounted, or
`SERVER_PATH` points somewhere else. Confirm `/Volumes/vislearnlab` exists.

**`KeyError: 'SERVER_PATH'`.** `SERVER_PATH` is not set in the repo-root `.env`.

**`ffmpeg not found`.** Install it in the conda env (`conda install ffmpeg`) or `pip install imageio-ffmpeg`.


## Folder Structure

| file | |
| --- | --- |
| `annotate_videos.py` | the annotation server and browser UI  |
| `select_validation_videos.py` | picks the validation sample — **already run, DONT TOUCH** |
| `validation_selection.csv` | the selected `subjID`, `trialID` pairs — committed |
| `validation_selection.txt` | readable record of the seed and what was picked |
| `video_claims.csv` | who holds which videos — gitignored, per-deployment |
| `.annotate.lock` | flock target — gitignored |
