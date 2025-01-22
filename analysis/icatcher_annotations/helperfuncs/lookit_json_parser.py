from datetime import datetime
import pandas as pd
from string import digits
import json
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
project_dir = os.environ.get("PROJECT_PATH")

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

def get_lookit_trial_times(lookit_json):
    syllable_info = pd.read_csv(os.path.join(project_dir, "data", "metadata", "syllables.csv"))
    audio_duration_info = pd.read_csv(os.path.join(project_dir, "data", "metadata", "audio_duration_info.csv"))
    carrier_onset = audio_duration_info.loc[0, 'silence_before']
    target_onset = carrier_onset + audio_duration_info.loc[0, 'carrier']
    f = open(lookit_json)
    study_info = json.load(f)

    # dataframe in which info will be accumulated
    trial_timing_info = pd.DataFrame()

    for session_info in study_info:
        child_id = session_info['child']['hashed_id']
        age_at_test = session_info['child']['age_rounded']
        gender = session_info['child']['gender']
        age_at_birth = session_info['child']['age_at_birth']
        language_list = session_info['child']['language_list']
        condition_list = session_info['child']['condition_list']
          
        fmt_str = r"%Y-%m-%dT%H:%M:%S.%f"
        # identify audio lag and trial information of each trials
        # TODO: add session information
        for key, value in session_info['exp_data'].items():
            # GENERALIZE THIS SECTION - WHICH KEYS 
            # only consider real trials that are 'easy' or 'hard', no attention getters (and no prematurely terminated trials)
            print(key)
            if ('easy' in key or 'hard' in key) and ('attention' not in key) and (len(value['eventTimings']) > 2):
                eventTypes = [timestamp_type['eventType'] for timestamp_type in value['eventTimings']]

                # get locations of videoStarted and videoPaused
                audioStartedIdx = ['startAudio' in event for event in eventTypes]
                videoStartedIdx = ['startRecording' in event for event in eventTypes]
                videoEndedIdx = ['trialComplete' in event for event in eventTypes]

                # find first place where 'videoStarted' and 'audioStarted' appear
                if any(videoStartedIdx):
                    video_start_idx = np.where(videoStartedIdx)[0][0]
                
                if any(audioStartedIdx):
                    audio_start_idx = np.where(audioStartedIdx)[0][0]
                
                if any(videoEndedIdx):
                    trial_end_idx = np.where(videoEndedIdx)[0][-1]

                for image in value["images"]:
                    # Extract the image name from the 'src' field (last part after '/')
                    image_name = image["src"].split("/")[-1].split(".")[0]  # Remove file extension
                    if image["position"] == "left":
                        left_image = image_name
                    elif image["position"] == "right":
                        right_image = image_name
                
                id_parts = key.split("-")
                trial_order = id_parts[0]
                trial_type = id_parts[1] + "-" + id_parts[4] if len(id_parts) > 4 else id_parts[1]
                
                [target_audio, target_image] = value["audioPlayed"].split("/")[-1].replace(".mp3", "").rsplit("_", 1)
                
                num_syllables = syllable_info[syllable_info['word'] == target_image]['syllable_count']
                target_offset = target_onset + audio_duration_info[audio_duration_info['syllables'] == num_syllables.iloc[0]]['target_word'].iloc[0]

                if any(videoStartedIdx) and any(audioStartedIdx):
                    trial_timestamps = \
                        [{'SubjectInfo.subjID': child_id, 'Trials.trialID': key.split("-",1)[1], \
                          'absolute_onset': datetime.strptime(value['eventTimings'][video_start_idx]['timestamp'][0:-1], fmt_str), \
                          'Trials.audio_lag_vs_video_lag': datetime.strptime(value['eventTimings'][audio_start_idx]['timestamp'][0:-1], fmt_str) - datetime.strptime(value['eventTimings'][video_start_idx]['timestamp'][0:-1], fmt_str),\
                          'absolute_offset': datetime.strptime(value['eventTimings'][trial_end_idx]['timestamp'][0:-1], fmt_str),
                          'SubjectInfo.testAge': age_at_test, \
                          'SubjectInfo.gender': gender, \
                          'Trials.leftImage': left_image,\
                          'Trials.rightImage': right_image, \
                          'Trials.targetImage': target_image, \
                          'Trials.targetAudio': target_audio, \
                          'Trials.trialType': trial_type, \
                          'Trials.carrier_onset': carrier_onset, \
                          'Trials.target_onset': target_onset, \
                          'Trials.target_offset': target_offset, \
                          'Trials.order': trial_order, \
                          'SubjectInfo.age_at_birth': age_at_birth, \
                          'SubjectInfo.language_list': language_list, \
                          'SubjectInfo.condition_list': condition_list
                          }]
                    print(trial_timestamps)
                    trial_timing_info = pd.concat([trial_timing_info, pd.DataFrame(trial_timestamps)])

    # get trial onset/offset relative to onset of video recording
    #trial_timing_info['Trials.onset'] = trial_timing_info['absolute_onset'] - trial_timing_info['video_onset'] 
    trial_timing_info['Trials.audio_lag_vs_video_lag'] = trial_timing_info['Trials.audio_lag_vs_video_lag'].apply(lambda x: x.total_seconds() * 1000)

    #trial_timing_info['Trials.offset'] = trial_timing_info['absolute_offset'] - trial_timing_info['video_onset'] 
    #trial_timing_info['Trials.offset'] = trial_timing_info['Trials.offset'].apply(lambda x: x.total_seconds() * 1000)

    # clean up trial type to be ready for parsing + add parentEnded
    trial_timing_info['Trials.trialType'] = trial_timing_info['Trials.trialType'].str.replace('\\d+-', '')

    # sort whole df by trial onset
    trial_timing_info.sort_values(by='Trials.order', inplace=True)

    # get trial number using absolute onsets
    trial_timing_info['Trials.ordinal'] = trial_timing_info.groupby('SubjectInfo.subjID').cumcount()+1

    return trial_timing_info