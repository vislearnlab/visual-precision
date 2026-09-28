"""Select the videos that will be manually annotated to validate iCatcher.

~20% of all videos in level-looks_source-icatcher_data.csv are chosen by taking every video from a
random set of participants (participants are added until the total is closest to the target fraction).
Only participants with at least --min-videos videos are eligible; the target is still a fraction of all videos.

Outputs (next to this script):
  validation_selection.csv  -> subjID, trialID (read by annotate_videos.py)
  validation_selection.txt  -> human-readable record of the seed and what was picked

Usage: python select_validation_videos.py [--seed 42] [--fraction 0.2] [--min-videos 16]
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ICATCHER_CSV = ROOT / 'data' / 'main' / 'data_to_analyze' / 'level-looks_source-icatcher_data.csv'
VIDEO_DIR = ROOT / 'data' / 'raw' / 'original_videos' / 'mp4'
SUBJ, TRIAL = 'SubjectInfo.subjID', 'Trials.trialID'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--fraction', type=float, default=0.2, help='total fraction of videos to select')
    ap.add_argument('--min-videos', type=int, default=16, help='only select participants with at least this many videos')
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    looks = pd.read_csv(ICATCHER_CSV, usecols=[SUBJ, TRIAL])
    videos = looks.drop_duplicates().sort_values([SUBJ, TRIAL]).reset_index(drop=True)
    # only videos that can actually be annotated
    exists = [(VIDEO_DIR / s / f'{t}_{s}.mp4').is_file() for s, t in zip(videos[SUBJ], videos[TRIAL])]
    missing = int(len(videos) - sum(exists))
    videos = videos[exists].reset_index(drop=True)

    n_videos = len(videos)
    total_target = round(args.fraction * n_videos)
    per_subj = videos.groupby(SUBJ).size()

    eligible = per_subj[per_subj >= args.min_videos]

    # random eligible participants, all of their videos, until closest to the target
    order = list(rng.permutation(eligible.index.to_numpy()))
    chosen, count = [], 0
    for subj in order:
        n = int(per_subj[subj])
        if count >= total_target or abs(count + n - total_target) > abs(count - total_target):
            break
        chosen.append(subj)
        count += n
    selection = videos[videos[SUBJ].isin(chosen)]
    selection.rename(columns={SUBJ: 'subjID', TRIAL: 'trialID'}).to_csv(HERE / 'validation_selection.csv', index=False)

    lines = [
        'iCatcher validation video selection',
        f'seed: {args.seed}',
        f'source: {ICATCHER_CSV.relative_to(ROOT)}',
        f'total videos: {n_videos} across {per_subj.size} participants'
        + (f' ({missing} in csv skipped: no mp4)' if missing else ''),
        f'eligible: {eligible.size} participants with >= {args.min_videos} videos ({int(eligible.sum())} videos)',
        f'target: {args.fraction:.0%} = {total_target} videos',
        f'selected: {len(selection)} videos ({len(selection) / n_videos:.1%}), '
        f'all videos from {len(chosen)} participants:',
        '',
    ]
    lines += [f'{s}\t{int(per_subj[s])} videos' for s in sorted(chosen)]
    (HERE / 'validation_selection.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines[:7]))


if __name__ == '__main__':
    main()
