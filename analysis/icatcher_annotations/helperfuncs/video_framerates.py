# source code adapted from Yotam Erel

import subprocess
from pathlib import Path
import json
import pickle

def get_frame_information(video_file_path, data_file_path):

    child_id = video_file_path.strip('.mp4').split('/')[-1]

    # if frame information already exists, return from data
    output_file = Path(data_file_path)
    if output_file.is_file():
        with open(data_file_path, 'r') as json_file:
            data = json.load(json_file)

        for vid in data:
            if vid['child'] == child_id:
                return vid['timestamps'], vid['num_frames']

    commands_list = [
        "ffprobe",
        "-show_frames",
        "-show_streams",
        "-print_format", "json",
        video_file_path
        ]  

    # run command on terminal and store output as a json file
    ffmpeg = subprocess.Popen(commands_list, stderr=subprocess.PIPE, stdout = subprocess.PIPE)
    output, err = ffmpeg.communicate()
    output = json.loads(output)

    frames = output.get('frames', [])
    # did not find video
    if not frames: 
        return [], []

    # filter out video frame info only 
    video_frames = [frame for frame in output['frames'] if frame['media_type'] == 'video']
    print(video_frames)
    frame_times = [frame["pkt_pts_time"] for frame in video_frames]
    video_stream_info = next(s for s in output['streams'] if s['codec_type'] == 'video')
    # assert len(frame_times) == int(video_stream_info["nb_frames"])

    # convert to milliseconds
    frame_times_ms = [int(1000*float(x)) for x in frame_times]
    # variable frame rate due to mp4 conversion
    #assert frame_times_ms[0] < 10.0

    # write to json if video information extracted
    if frame_times_ms:
        write_to_json(child_id, frame_times_ms, int(video_stream_info["nb_frames"]), data_file_path)

    # returns timestamps in milliseconds
    return frame_times_ms, int(video_stream_info["nb_frames"])

# did not include: video_stream_info["time_base"] 


def write_to_json(child_id, timestamps, num_frames, filename):
    """
    checks if output file is in directory. if not, writes new JSON file
    consisting of an array of dictionaries. Adds 
    {child: child_id, timestamps: timestamps, num_frames: numframes} if
    child_id not already in data.
    
    child_id (string): unique child ID associated with subject
    timestamps (List[int]):
    num_frames (int): number of frames in the video
    rtype: None
    """
    vid_data = {
        'child': child_id,
        'timestamps': timestamps,
        'num_frames': num_frames
    }

    output_file = Path(filename)

    # if no data file with name filename exists, create new array 
    if output_file.is_file():
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
    else:
        data = []

    # write data if child not already in data
    if not any([child_id in x['child'] for x in data]):
        data.append(vid_data)
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)

    return

    

#if __name__ == "__main__":
#    vid_path = "../TEMP_video/3GSKJ5.mp4"
#    timestamps = get_frame_information(vid_path)[0]
