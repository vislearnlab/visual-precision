#!/bin/bash

# prupose: submit array of jobs to run icatcher individually for all videos in video_dir specified below

# example usage: 
# ./run_icatcher_job_array.sh 
# ^^ runs ALL VIDEOS 

# or: 
# ./run_icatcher_job_array.sh SAXE_XNV_233_GazeVideo.mp4 SAXE_XNV_244_GazeVideo.mp4 
# ^^ runs ONLY file names provided as arguments

source ../../.env

video_dir="$PROJECT_PATH/data/raw/original_videos/mp4"
icatcher_scripts_path="$PROJECT_PATH/preprocessing/2_run_icatcher"

#if no files given as arguments
if [ $# -eq 0 ]; then
    videos=( $(find $video_dir/ -not -path '*/._*' -type f -name "*.mp4") )
else
# else, use arguments input as videos
    base_videos=("${@:1}")
    videos=("${base_videos[@]/#/$video_dir}")
fi

len=$(expr ${#videos[@]} - 1) 

cmd="sbatch --array=0-$len $icatcher_scripts_path/run_icatcher.sh $PROJECT_PATH ${videos[@]}"

echo $cmd

$cmd
