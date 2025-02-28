import os
import subprocess
import re
import json
import csv
from config import PROJECT_PATH, SERVER_PATH
hashed_ids = {}

# Making a map of the response UUIDs to the child hashed IDs for easier storage
def hashed_id_map(responses_path):
    with open(responses_path, 'r') as file:
        response_data = json.load(file)
    print(response_data)
    for response in response_data:
        hashed_ids[response["response"]["uuid"]] = response["child"]["hashed_id"]

# Ensure that clean Lookit JSON file does not include any identifiable subject data
def clean_lookit_json(input_lookit_json, cleaned_path, subject_data_path):
    f = open(input_lookit_json)
    lookit_json = json.load(f)
    identifiable_fields = ['birthday', 'age_in_days', 'name', 'global_id', 'nickname']
    child_subject_fields = ['name', 'birthday', 'age_in_days', 'global_id', 'age_at_birth', 'age_rounded','gender']
    subject_csv_rows = []
    subject_csv_header = ['local_id', 'hashed_id'] + child_subject_fields + ['parent_nickname', 'parent_global_id', 'parent_hashed_id', 'date_created', 'response_id']
    local_id_count = 0
    # Read existing hashed IDs in subject_data.csv
    existing_hashed_ids = set()
    if os.path.exists(subject_data_path):
        with open(subject_data_path, 'r') as csvfile:
            existing_hashed_ids = {row['hashed_id'] for row in csv.DictReader(csvfile)}

    for session in lookit_json:
        local_id_count += 1
        # Skipping if the hashed_id already exists in subject_data.csv or if the hashed_id is not in the session data
        if 'child' in session and 'hashed_id' in session['child']:
            hashed_id = session['child']['hashed_id']
            if hashed_id in existing_hashed_ids:
                continue
                
            # Build row data: adding a local_id which is a unique identifier for each row in the CSV file in the format VVIXX where XX is the subject number
            row_data = {'local_id': f"VVI{'0' if local_id_count < 10 else ''}{local_id_count}", 'hashed_id': hashed_id}
            row_data.update({field: session['child'].get(field, '') for field in child_subject_fields})
            
            if 'participant' in session:
                row_data.update({
                    'parent_nickname': session['participant'].get('nickname', ''),
                    'parent_global_id': session['participant'].get('global_id', ''),
                    'parent_hashed_id': session['participant'].get('hashed_id', '')
                })
            else:
                row_data.update({'parent_nickname': '', 'parent_global_id': '', 'parent_hashed_id': ''})
             
            if 'response' in session:
                row_data.update({
                    'date_created': session['response']['date_created'].split(" ")[0],
                    'response_id': session['response']['uuid']
                })
            
            subject_csv_rows.append(row_data)

        # Remove identifiable data
        for field in identifiable_fields:
            session['child'].pop(field, None)
            if 'participant' in session:
                session['participant'].pop(field, None)

        # Remove birthDate from exp_data
        if 'exp_data' in session:
            for key in session['exp_data']:
                session['exp_data'][key].pop('birthDate', None)

    # Write to CSV file, appending if it exists
    mode = 'a' if os.path.exists(subject_data_path) else 'w'
    if mode == 'a':
        with open(subject_data_path, 'a') as f:
            f.seek(0, 2)  # Move the pointer to the end of the file
            f.write('\n')  # Add a new line if it's not empty
    with open(subject_data_path, mode, newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=subject_csv_header)
        if mode == 'w':  # Only write header for new files
            writer.writeheader()
        writer.writerows(subject_csv_rows)

    # Save cleaned data
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
            r'\d+_\d+(?:\s\(\d\))?\.webm$'   # Ensure correct ending format, optionally match duplicate videos
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
    # Storing the identifiable data in a separate file
    identifiable_data_path = os.path.join(raw_server_dir, "lookit", "subject_data.csv")
    # Clean the lookit_study.json file to remove identifiable data and place in a separate file
    clean_lookit_json(input_lookit_responses_path, lookit_responses_path, identifiable_data_path)
    # Specify the directory containing .webm files
    videos_path = os.path.join(raw_server_dir, "original_videos")
    # Make a map of the response UUIDs to the child hashed IDs for easier storage: videos are coming in from Lookit with response UUIDs
    hashed_id_map(lookit_responses_path)
    # Convert the .webm files to .mp4 files
    convert_webm_to_mp4(os.path.join(videos_path, "webm"), os.path.join(videos_path, "mp4"))
    # Sanity check that each participant directory has at least 34 videos
    mp4_dir = os.path.join(videos_path, "mp4")
    for child_dir in os.listdir(mp4_dir):
        child_path = os.path.join(mp4_dir, child_dir)
        if os.path.isdir(child_path):
            mp4_files = [f for f in os.listdir(child_path) if f.endswith('.mp4')]
            if len(mp4_files) < 34:
                print(f"Warning: Directory {child_dir} has {len(mp4_files)} videos instead of expected 34")

if __name__ == "__main__":
    preprocess_raw_data()