#!/usr/bin/env python3
"""
Local runner for processing videos with GPU and a progress bar.

Usage examples:
  ./run_icatcher_local.py \
    --gpu_id 0 
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
VIDEO_EXTS = {'.mp4'}

def find_videos(path: Path) -> List[Path]:
    files = []
    for p in path.rglob('*'):
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS and not p.name.startswith('.'):
            files.append(p)
    return sorted(files)

def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

def should_skip(output_video: Path, output_annotations: Path, process_existing: bool) -> bool:
    if not process_existing and Path(output_video).exists() and Path(output_annotations).exists():
        return True
    return False

def run_command(project_path: Path, input_path: Path, gpu_id: int, timeout: Optional[int]=60) -> int:
    cmd = ["bash", "./run_icatcher_local.sh", str(project_path), str(input_path), str(gpu_id)]
    # execute in shell to allow complex commands; user is responsible for safety
    env = os.environ.copy()
    try:
        completed = subprocess.run(cmd, shell=False, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        if completed.returncode != 0:
            print(f"Command failed for {input_path} (rc={completed.returncode})", file=sys.stderr)
            print(completed.stderr.decode(errors='replace'), file=sys.stderr)
        return completed.returncode
    except subprocess.TimeoutExpired:
        print(f"Command timed out for {input_path}", file=sys.stderr)
        return 124


def parse_args():
    p = argparse.ArgumentParser(description="Run icatcher-like processing locally using a GPU and progress bar")
    p.add_argument('--gpu-id', type=int, default=0, help='Force GPU id')
    p.add_argument('--input-dir', type=str, default=None, help='Input directory path')
    p.add_argument('--output-dir', type=str, default=None, help='Output directory path')
    p.add_argument('--process-existing', action='store_true', help='Process videos when output already exists')
    return p.parse_args()

def main():
    args = parse_args()
    project_path = os.environ.get('PROJECT_PATH')
    if not project_path:
        print("PROJECT_PATH environment variable is not set", file=sys.stderr)
        sys.exit(1)
    if args.input_dir:
        input_dir = Path(args.input_dir)
    else:
        input_dir = Path(project_path) / 'data' / 'raw' / 'original_videos' / 'mp4'

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(project_path) / 'data' / 'raw'

    output_annotations = output_dir / 'icatcher_annotations'
    output_videos = output_dir / 'icatcher_videos'
    os.makedirs(output_annotations, exist_ok=True)
    os.makedirs(output_videos, exist_ok=True)
    videos = find_videos(input_dir)
    if not videos:
        print(f"No videos found in {input_dir}")
        return
    else:
        print(f"Found {len(videos)} videos in {input_dir}")
    errors = 0
    # first filter out all the videos that have already been processed to have the correct progress bar
    unprocessed_videos = []
    for video in videos:
        output_video= f"{output_videos}/{video.parent.name}/{video.stem}_output.mp4"
        output_annotation=f"{output_annotations}/{video.parent.name}/{video.stem}.npz"
        if not should_skip(output_video, output_annotation, args.process_existing):
            unprocessed_videos.append(video)

    with tqdm(total=len(unprocessed_videos), unit='video') as pbar:
        for video in unprocessed_videos:
            rc = run_command(project_path, video, args.gpu_id)
            if rc != 0:
                errors += 1
            pbar.update(1)

    if errors:
        print(f"Finished with {errors} errors", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
