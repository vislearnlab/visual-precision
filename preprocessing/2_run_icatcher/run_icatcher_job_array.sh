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
output_videos_path="$project_path/data/raw/icatcher_videos"

#if no files given as arguments
if [ $# -eq 0 ]; then
    videos=()
    
    # Iterate through each parent_base directory in video_dir
    for parent_base in $(find "$video_dir" -mindepth 1 -maxdepth 1 -type d -printf "%f\n"); do
        input_parent_path="$video_dir/$parent_base"
        output_parent_path="$output_videos_path/$parent_base"

        # Ensure the output directory exists
        mkdir -p "$output_parent_path"

        # Iterate over mp4 files in the parent_base directory
        for input_video in "$input_parent_path"/*.mp4; do
            [ -e "$input_video" ] || continue  # Skip if no .mp4 files exist

            filename=$(basename -- "$input_video")  # Extract filename (e.g., "123.mp4")
            trial_id="${filename%.mp4}"  # Remove .mp4 extension (e.g., "123")
            output_video="$output_parent_path/${trial_id}_output.mp4"

            # Add to the list only if the output file does NOT exist
            if [ ! -e "$output_video" ]; then
                videos+=("$input_video")
            fi
        done
    done
else
# else, use arguments input as videos
    base_videos=("${@:1}")
    videos=("${base_videos[@]/#/$video_dir}")
fi

len=$(expr ${#videos[@]} - 1) 

cmd="sbatch --array=0-$len $icatcher_scripts_path/run_icatcher.sh $PROJECT_PATH ${videos[@]}"

echo $cmd

$cmd
