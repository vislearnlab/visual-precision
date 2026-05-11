# How precise is infants' visual concept knowledge?
Stimuli, data and analysis for a study on the precision of the visual concept knowledge of infants between the ages of 14- and 24-month-olds. (Pre-registration: https://osf.io/xc986). 

Below are brief descriptions of the main sections of the repository and instructions on how to reproduce the coding process. 

## Stimuli 
This folder contains the stimuli used for the study we ran on Children Helping Science/Lookit. The stimuli for experiment 1 were derived from a set of stimuli used by [Long et al., in prep.](https://jov.arvojournals.org/article.aspx?articleid=2800958) for older children and adults. That original set of trials can be found in the `older_stimuli` folder in `lookit/preprocessing`. Then, make sure to run `helpers.R` in your environment before running through `preprocessing_sample1.qmd` and `preprocessing_sample2.qmd` to create the `lookit_stimuli.json` file within that directory and the `level-imagepair_data.csv` files found in `data/metadata`. All of the stimuli used for this study are stored in `exp1` in a folder structure that matches what Children Helping Science expects for stimuli. We host these stimuli, along with our instructions files, which are too big to store on GitHub, on an Ubuntu server in a public file directory that is linked to in our JavaScript study.

## Experiment
This folder contains the JavaScript code for the asynchronous experiment we run on Children Helping Science, using the in-built JavaScript protocol generator. The `lookit_stimuli.json` files in `stimuli/metadata` are the JSON used to set the main trial order, with some partial randomization to the trial and image ordering. This folder also contains example frames from the experiment (it does not include frames where the order is flipped), which are used to calculate saliency differences and a compensation script to pay participants on Children Helping Science. For the second sample, there is some additional logic in the compensation script to remind participants to complete an optional vocabulary survey.

## Preprocessing
This folder contains the pre-processing code for processing the videos and trial JSON from Children Helping Science by moving the files to our server, converting the video format, running the videos through iCatcher+ for automated gaze coding and then converting the iCatcher+ to a readable format in `data/data_to_analyze`. You will additionally need [ffmpeg](https://www.ffmpeg.org/) to run through the preprocessing pipeline. 

## Analysis
This folder contains (1) the R code that we use to process the gaze data from iCatcher+, create plots and run our statistical analyses and (2) the Matlab code we use to measure saliency differences between image pairs using the GBVS toolbox. It also contains the power analysis we conducted to determine the sample size we needed for our study. 

## Models
This folder contains the Python code we use to generate our model embeddings to use as measures of similarity between image-pairs.

## Writing
This folder contains a draft of the results section generated in R Markdown.

## Data
The data folder contains all levels of data from raw through processed. The raw videos and iCatcher+ processed videos which are inherently identifiable are not shared here. The preprocessed cleaned iCatcher+ and trial-level data, generated from running through `preprocessing/3_process_icatcher_output/main.ipynb`, is in the `data_to_analyze` folders while the processed data, generated during analysis, is in the `processed_data` folders. 

More information on the data to be found in the dataset_description.json file that is being worked on. 

## Running through the pipeline
Since the videos we collected are inherently identifiable (and large) we cannot share them, so we recommend starting at the analysis section if you do not have a set of videos. In general, please install Python packages using the `requirements.txt` file in the main directory to get started. Then, refer to the Markdown files in the `preprocessing` and `analysis` subdirectories.

1. Downloading the video ZIP and trial JSON files from Children Helping Science.
 - unzip the videos and store them in `data/raw/raw_videos` locally 
 - Install `ffmpeg` to be able to convert webm to mp4
 - Place the trial JSON file as `data/lookit/<sample>/input_lookit_study_data.json` on the **server**, where sample is either 'sample1' or 'sample2' depending on which sample you are processing. 
 - Connect to VPN and Polygon
 - Copy over the `.env_template` file into a `.env` file, filling out the rows as required. 
 - Run `preprocess.py` (which calls `preprocessing/utils/move_to_polygon.py` and `preprocessing/1_preprocess_raw_data.py`) to move the videos to the server and then format the raw videos and clean the Lookit JSON file. 
 - (Optional) You can also run this first locally to move files to the server and then run it on the `tversky` server to preprocess raw data faster.
 - **Note:** in the past this has been run on the `SSRDE server` as well

2. Run iCatcher+ and annotate gaze data across the formatted videos
- Navigate to `preprocessing/2_run_icatcher`
- Activate the conda environment `conda activate visualprecision`
- Install the requirements `pip install -r requirements.txt`
- Run `python run_icatcher_local.py --gpu_id 0` on a server with a GPU like Tversky. 
- See `preprocessing/2_run_icatcher/README.md` for a more detailed setup instruction and troubleshooting if needed.


3. After iCatcher+ has finished running
- run `preprocessing/3_process_icatcher_output/main.ipnyb` to process the iCatcher+ data into a single CSV file. 
- **Note:** You will probably want to run this locally so that you can run downstream analysis files locally as well


4. Run the following to generate model inputs *(optional if these values have already been calculated)*:
- Run `models/main.py` to generate embedding similarities
- Run `analysis/saliency/visualize_maps.m` to generate saliency differences

5. Run the Quarto files in `analysis` in the order that they are numbered.