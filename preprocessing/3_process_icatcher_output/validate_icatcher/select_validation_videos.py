"""Select the videos that will be manually annotated to validate iCatcher.

20% of all videos in level-looks_source-icatcher_data.csv are chosen:
  * 10%: every video from a random set of participants
  * 10%: random videos drawn across the remaining participants

Outputs (next to this script):
  validation_selection.csv  -> subjID, trialID, selection_type (read by annotate_videos.py)
  validation_selection.txt  -> human-readable record of the seed and what was picked

Usage: python select_validation_videos.py [--seed 42] [--fraction 0.2]
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
    half_target = round(total_target / 2)
    per_subj = videos.groupby(SUBJ).size()

    # 1) random participants, all of their videos, until closest to half the target
    order = list(rng.permutation(per_subj.index.to_numpy()))
    chosen, count = [], 0
    for subj in order:
        n = int(per_subj[subj])
        if count >= half_target or abs(count + n - half_target) > abs(count - half_target):
            break
        chosen.append(subj)
        count += n
    part_videos = videos[videos[SUBJ].isin(chosen)].assign(selection_type='participant')

    # 2) random videos across the remaining participants to fill up to the total target
    rest = videos[~videos[SUBJ].isin(chosen)]
    n_random = min(total_target - len(part_videos), len(rest))
    idx = rng.choice(len(rest), size=n_random, replace=False)
    rand_videos = rest.iloc[np.sort(idx)].assign(selection_type='random')

    selection = pd.concat([part_videos, rand_videos], ignore_index=True)
    selection.rename(columns={SUBJ: 'subjID', TRIAL: 'trialID'}).to_csv(HERE / 'validation_selection.csv', index=False)

    lines = [
        'iCatcher validation video selection',
        f'seed: {args.seed}',
        f'source: {ICATCHER_CSV.relative_to(ROOT)}',
        f'total videos: {n_videos} across {per_subj.size} participants'
        + (f' ({missing} in csv skipped: no mp4)' if missing else ''),
        f'target: {args.fraction:.0%} = {total_target} videos',
        f'selected: {len(selection)} videos ({len(selection) / n_videos:.1%})',
        '',
        f'Participant set: {len(part_videos)} videos ({len(part_videos) / n_videos:.1%}), '
        f'all videos from {len(chosen)} participants:',
        ', '.join(sorted(chosen)),
        '',
        f'Random set: {len(rand_videos)} videos ({len(rand_videos) / n_videos:.1%}) '
        f'from {rand_videos[SUBJ].nunique()} participants not in the participant set:',
    ]
    lines += [f'{s}\t{t}' for s, t in zip(rand_videos[SUBJ], rand_videos[TRIAL])]
    (HERE / 'validation_selection.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines[:8]))


if __name__ == '__main__':
    main()
