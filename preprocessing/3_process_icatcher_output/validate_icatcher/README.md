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
3. Pick your mode in `annotate_videos.py` (see [Two run modes](#two-run-modes)) — SSH to Tversky is the default
4. `python annotate_videos.py`
5. On your laptop: `ssh -L 8765:localhost:8765 tversky`, then open <http://localhost:8765>
6. Enter your username and start labeling. Keys are listed at the bottom of the page.

---

## Two run modes

The scripts can read the videos and iCatcher csv either from the

- a. server filesystem (when you are
SSHed into it) 
- b. from a volume mounted on your laptop

Three paired lines near the top of `annotate_videos.py` switch between them, so uncomment one of each pair (currently defaulted to SSH):

```python
ROOT = HERE.parents[2]                 # Use if on SSH
# ROOT = Path(os.environ['SERVER_PATH']) # Use if connected to server volume

CLAIMS_CSV = HERE / 'video_claims.csv'          # Use if on SSH
# CLAIMS_CSV = DATA_DIR / 'video_claims.csv'    # Use if connected to server volume
LOCK_FILE = HERE / '.annotate.lock'             # Use if on SSH
# LOCK_FILE = DATA_DIR / '.annotate.lock'       # Use if connected to server volume
```

`select_validation_videos.py` has the same `ROOT` pair.

**SSH to Tversky (default).** Everyone works in the one checkout on the server, so `HERE` is the same
directory for all annotators and the claims file and lock are shared for free. Videos are read from
local disk, so ffmpeg decoding is fast. This is the mode the tool was written for.

**Polygon volume mounted.** Connect to the VPN and mount the share, set `SERVER_PATH` in `.env`, and
run on your own laptop with no tunnel. Because each laptop has its own checkout, `HERE` is **not**
shared — the `DATA_DIR` variants put the claims file and lock on the volume so separate laptops still
coordinate. See [Concurrency](#concurrency) for what is and isn't guaranteed here.

## Requirements

- `pandas` and `python-dotenv`
- `ffmpeg` on `PATH`, or `pip install imageio-ffmpeg`
- For **volume mode only**: `SERVER_PATH` set in the repo-root `.env`

## How work is handed out

Annotators are identified by the username typed on the login screen,

Videos are claimed **a participant at a time**: when you need new work the tool claims every selected
video of the next unclaimed participant, and you work through all ~32 of them in a row before moving
on. Claims are recorded in `video_claims.csv` and claimed videos are never offered to anyone else.

`video_claims.csv` is gitignored. It is a per-deployment state, not repo content. It lives only on the
machine (tversky) which is connected to the volume (polygon) you are running against, so **don't delete it**.

## Concurrency

In SSH mode the `flock` is genuinely shared and simultaneous annotators serialise their writes.

In volume mode this holds **only if** you switched `LOCK_FILE` to the `DATA_DIR` variant, otherwise
each laptop locks its own file while writing the same csv on the share.

## How the selection was made

`select_validation_videos.py` picks ~20% of all videos by choosing whole random participants with the minimum amout of valid videos.

The committed result is 1492 videos (19.9%) from 47 participants at `--seed 42`;
`validation_selection.txt` is the human-readable record.

**Do not re-run it -> see the warning at the top of this file.**

## Troubleshooting

**Port already in use / stale UI.** `annotate_videos.py` scans ports 8765–8814 and prints the one it
got. A leftover process still holding 8765 means the new instance lands on 8766 while your tunnel and
browser still point at 8765 — you would be annotating against the old process. Check with
`lsof -nP -iTCP:8765 -sTCP:LISTEN` and kill the stale pid before starting.

**`FileNotFoundError` on `level-looks_source-icatcher_data.csv`.** Wrong mode for where you are
running: either the `ROOT` toggle is on SSH while you are on your laptop, or the volume is not
mounted. Confirm `/Volumes/vislearnlab` exists for volume mode.

**`KeyError: 'SERVER_PATH'`.** Volume mode is selected but `SERVER_PATH` is not set in `.env`.

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
