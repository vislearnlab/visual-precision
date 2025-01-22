import os
import subprocess
import re
import json
from dotenv import load_dotenv

load_dotenv()
project_dir = os.environ.get("PROJECT_PATH")
hashed_ids = {}

# Making a map of the response UUIDs to the child hashed IDs for easier storage
def hashed_id_map(responses_path):
    with open(responses_path, 'r') as file:
        response_data = json.load(file)
    print(response_data)
    for response in response_data:
        hashed_ids[response["response"]["uuid"]] = response["child"]["hashed_id"]

def convert_webm_to_mp4(input_path, output_path):
    # Ensure the directory exists
    if not os.path.exists(input_path):
        print(f"Directory {input_path} does not exist.")
        return

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Loop through files in the directory
    for file in os.listdir(input_path):
        # Pattern of videos coming in from Lookit
        pattern = (
            r'^videoStream_'                 # Match "videoStream_"
            r'([a-f0-9-]{36})_'              # Match the study UUID
            r'(\d+-[a-zA-Z0-9-]+)_'          # Match the trial ID (ex: 38-easy-turkey-swan)
            r'([a-f0-9-]{36})_'              # Match the response UUID
            r'\d+_\d+\.webm$'                # Ensure correct ending format
        )
        matches = re.match(pattern, file)
        # Not using any consent video files
        if matches and "consent" not in file:
            input_file = os.path.join(input_path, file)
            if matches.group(3) in hashed_ids:
                hashed_child_id = hashed_ids[matches.group(3)]
            else:
                print(f"Skipping response {matches.group(3)}")
                continue
            os.makedirs(os.path.join(output_path, hashed_child_id), exist_ok=True)
            # Not including trial ordering number in file names since it is not a primary key
            output_file = os.path.join(output_path, hashed_child_id, f"{matches.group(2).split("-",1)[1]}_{hashed_child_id}.mp4")
            # Do not convert files that have already been converted
            if (os.path.exists(output_file)):
                continue
            # FFmpeg command
            command = [
                "ffmpeg",
                "-i", input_file,
                "-b:v", "3M", # Set video bitrate to 3 Mbps
                "-vsync", "2",
           #     "-c:v", "libx264",
           #     "-c:a", "aac",
                output_file
            ]

            print(f"Converting: {input_file} -> {output_file}")
            try:
                subprocess.run(command, check=True)
                print(f"Successfully converted: {file}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting {file}: {e}")

# Specify the directory containing .webm files
print(project_dir)
lookit_responses = os.path.join(project_dir, "data", "metadata", "lookit_study.json")
videos_path = os.path.join(project_dir, "data", "original_videos")
hashed_id_map(lookit_responses)
convert_webm_to_mp4(os.path.join(videos_path, "webm"), os.path.join(videos_path, "mp4"))
