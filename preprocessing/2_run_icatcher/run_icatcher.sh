#!/bin/bash
#SBATCH --mail-type=END
#SBATCH --mem=32GB
#SBATCH --output=icatcher.%A_%a.out
#SBATCH --time=10:00:00

#purpose: run icatcher for one video

project_path=$1
icatcher_scripts_path="$project_path/preprocessing/2_run_icatcher"
output_annotations_path="$project_path/data/raw/icatcher_annotations"
output_videos_path="$project_path/data/raw/icatcher_videos"
echo $icatcher_scripts_path
gazevideo_file="$icatcher_scripts_path/gazevideo_info.csv"

videos=("${@:2}")

current_video=${videos[${SLURM_ARRAY_TASK_ID}]}

video_base="$(basename -- $current_video)"
video_base="${video_base%.*}"
parent_base="$(basename -- "$(dirname -- "$current_video")")"

echo 'video base:'
echo $video_base

cropamt=`awk -F',' -v lvar="$video_base" '$1~lvar {print $2}' $gazevideo_file`

if [ -z "$cropamt" ]; then
    cropamt=0
fi

echo 'crop amount:'
echo $cropamt

cropside=`awk -F',' -v lvar="$video_base" '$1~lvar {print $3}' $gazevideo_file`
cropside="${cropside/$'\r'/}"

if [ -z "$cropside" ]; then
    cropside="top"
fi

echo 'cropside:'
echo $cropside

face_classifier=`awk -F',' -v lvar="$video_base" '$1~lvar {print $4}' $gazevideo_file`
face_classifier="${face_classifier/$'\r'/}"

if [ -z "$face_classifier" ]; then
    face_classifier="lowest"
fi

echo 'face_classifier:'
echo $face_classifier
echo $current_video

full_output_videos_path="$output_videos_path/$parent_base"
mkdir -p "$full_output_videos_path"
full_output_annotations_path="$output_annotations_path/$parent_base"
mkdir -p "$full_output_annotations_path"

output_video="$full_output_videos_path/${video_base}_output.mp4"
output_annotations="$full_output_annotations_path/${video_base}.npz"
echo "Output video path:"
echo $output_video
echo "Output annotations path:"
echo $output_annotations

# Check if both output files exist for this video
if [[ -f "$output_video" && -f "$output_annotations" ]]; then
    echo "Output files for $video_base exist. Skipping execution."
    exit 0
fi

# If the video output file has been deleted, get rid of annotations file too to prevent errors
if [[ ! -f "$output_video" && -f "$output_annotations" ]]; then
    echo "Deleting $output_annotations as output video file does not exist."
    rm -rf "$output_annotations"
fi

if [[ "$face_classifier" = "baby" ]] ; then
    cmd="icatcher $current_video --use_fc_model --illegal_transitions_path $icatcher_scripts_path/illegal_transitions.csv --output_annotation $full_output_annotations_path --output_format compressed --output_video_path $full_output_videos_path --crop_percent $cropamt --crop_mode $cropside --gpu_id 0"
elif [[ "$face_classifier" = "lowest" ]] ; then
    cmd="icatcher $current_video --output_annotation $full_output_annotations_path --output_format compressed --output_video_path $full_output_videos_path --crop_percent $cropamt --crop_mode $cropside --gpu_id 0"
fi
echo $cmd 

$cmd
