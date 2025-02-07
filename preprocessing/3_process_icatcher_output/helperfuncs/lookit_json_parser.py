from datetime import datetime
import pandas as pd
from string import digits
import json
import numpy as np
import os
from config import *

def get_lookit_trial_times(lookit_json):
    audio_duration_info = pd.read_csv(os.path.join(PROJECT_PATH, "data", "metadata", "level-syllables_added-audio_data.csv"))
    subject_sections = pd.read_csv(os.path.join(PROJECT_PATH, "data", "metadata", "level-section_data.csv"))
    word_onset_syllable_info = pd.read_csv(os.path.join(PROJECT_PATH, "data", "metadata", "level-wordtype_added-audio_data.csv"))
    # Get section info for this project
    section_row = subject_sections[subject_sections['section_name'] == PROJECT_VERSION].iloc[0]
    start_date = datetime.strptime(section_row['start_date'], '%Y-%m-%d')
    end_date = section_row['end_date']
    if end_date and not pd.isna(end_date):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    carrier_onset = audio_duration_info.loc[0, 'silence_before']
    target_onset = carrier_onset + audio_duration_info.loc[0, 'carrier']
    f = open(lookit_json)
    study_info = json.load(f)

    # dataframe in which info will be accumulated
    trial_timing_info = pd.DataFrame()

    for session_info in study_info:
        print(session_info.keys())
        # Parse session date and check if it is within the data collection bounds of the project version
        session_date = datetime.strptime(session_info['response']['date_created'].split()[0], '%Y-%m-%d')
        if session_date <= start_date:
            continue
        if end_date and not pd.isna(end_date) and session_date >= end_date:
            continue
        child_id = session_info['child']['hashed_id']
        age_at_test = session_info['child']['age_rounded']
        gender = session_info['child']['gender']
        age_at_birth = session_info['child']['age_at_birth']
        language_list = session_info['child']['language_list']
        condition_list = session_info['child']['condition_list']
          
        fmt_str = r"%Y-%m-%dT%H:%M:%S.%f"
        # identify audio lag and trial information of each trials
        # TODO: modularize this section
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
                
                # Determine which word to match based on target_audio: 'find' and 'see' are question phrases and use a different version of the same word 
                if target_audio in ['find', 'see']:
                    match_word = f"{target_image}2"
                else:
                    match_word = target_image
                    
                # Get onset info by matching word column
                current_onset_syllable_info = word_onset_syllable_info[word_onset_syllable_info['word'] == match_word]
                if not current_onset_syllable_info.empty:
                    article_length = current_onset_syllable_info['article_length'].iloc[0]
                    current_target_onset = target_onset + article_length
                else:
                    print(f"No onset info found for word: {match_word}")
                
                num_syllables = current_onset_syllable_info['syllable_count']
                target_offset = current_target_onset + audio_duration_info[audio_duration_info['syllables'] == num_syllables.iloc[0]]['target_word'].iloc[0]

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
                          'Trials.target_onset': current_target_onset, \
                          'Trials.target_offset': target_offset, \
                          'Trials.article_length': article_length if article_length else 0, \
                          'Trials.order': trial_order, \
                          'SubjectInfo.age_at_birth': age_at_birth, \
                          'SubjectInfo.language_list': language_list, \
                          'SubjectInfo.condition_list': condition_list
                          }]
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