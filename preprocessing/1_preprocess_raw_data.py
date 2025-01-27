import os
import subprocess
import re
import json
from ..config import PROJECT_PATH, SERVER_PATH, PROJECT_VERSION
hashed_ids = {}

# Making a map of the response UUIDs to the child hashed IDs for easier storage
def hashed_id_map(responses_path):
    with open(responses_path, 'r') as file:
        response_data = json.load(file)
    print(response_data)
    for response in response_data:
        hashed_ids[response["response"]["uuid"]] = response["child"]["hashed_id"]

# Ensure that clean Lookit JSON file does not include any identifiable data
def clean_lookit_json(input_lookit_json, cleaned_path):
    f = open(input_lookit_json)
    lookit_json = json.load(f)
    identifiable_fields = ['birthday', 'age_in_days', 'name', 'global_id', 'nickname']
    for session in lookit_json:
        # Removing identifiable data relating to child
        if 'child' in session:
            for field in identifiable_fields:
                session['child'].pop(field, None)
        # Removing identifiable data relating to parent/guardian
        if 'participant' in session:
            for field in identifiable_fields:
                session['participant'].pop(field, None)
        # Sometimes 'birthDate' field is included in an exit survey which may have different key depending on the individual experiment design
        if 'exp_data' in session:
            for key in session['exp_data']:
                session['exp_data'][key].pop('birthDate', None)
    with open(cleaned_path, 'w') as f:
        json.dump(lookit_json, f, indent=4)
    return lookit_json

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

def preprocess_raw_data():  
    raw_project_dir = os.path.join(PROJECT_PATH, "data", "raw")
    raw_server_dir = os.path.join(SERVER_PATH, "data", "raw")
    # Only storing the input_lookit_study.json file in the server directory since it might contain identifiable data
    input_lookit_responses_path = os.path.join(raw_server_dir, "lookit", "input_lookit_study.json")
    # Storing the lookit_study.json file in the project directory since it does not contain identifiable data
    lookit_responses_path = os.path.join(raw_project_dir, "lookit", "lookit_study.json")
    # Clean the lookit_study.json file to remove identifiable data
    clean_lookit_json(input_lookit_responses_path, lookit_responses_path)
    # Specify the directory containing .webm files
    videos_path = os.path.join(raw_server_dir, "original_videos")
    # Make a map of the response UUIDs to the child hashed IDs for easier storage: videos are coming in from Lookit with response UUIDs
    hashed_id_map(lookit_responses_path)
    # Convert the .webm files to .mp4 files
    convert_webm_to_mp4(os.path.join(videos_path, "webm"), os.path.join(videos_path, "mp4"))

if __name__ == "__main__":
    preprocess_raw_data()