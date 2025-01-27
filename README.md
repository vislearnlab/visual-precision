# How precise is infants' visual concept knowledge?
Stimuli, data and analysis for a study on the precision of the visual concept knowledge of infants between the ages of 14- and 24-month-olds. (Pre-registration: https://osf.io/xc986). 

Below are brief descriptions of the main sections of the repository and instructions on how to reproduce the coding process. 

## Stimuli 
This folder contains the stimuli used for the study we ran on Children Helping Science/Lookit. The stimuli were derived from a set of stimuli used by [Long et al., in prep.](https://jov.arvojournals.org/article.aspx?articleid=2800958) for older children and adults. That original set of trials can be found in the `older_stimuli` folder in `lookit/preprocessing`. Then, make sure to run `helpers.R` in your environment before running through `preprocessing.qmd` to create the `stimuli.csv` and `stimuli.json` files found in `data/metadata`. All of the stimuli used for this study are stored in `exp1` in a folder structure that matches what Children Helping Science expects for stimuli. We host these stimuli, along with our instructions files, which are too big to store on GitHub, on an Ubuntu server in a public file directory that is linked to in our JavaScript study.

## Experiment
This folder contains the JavaScript code for the asynchronous experiment we run on Children Helping Science, using the in-built JavaScript protocol generator. The `stimuli.json` file in `data/metadata` is the JSON used to set the main trial order, with some partial randomization to the trial and image ordering.

## Preprocessing
This folder contains the pre-processing code for processing the videos and trial JSON from Children Helping Science by converting the video format, running the videos through iCatcher+ for automated gaze coding and then converting the iCatcher+ to a readable format in `data/data_to_analyze`. You will additionally need [ffmpeg](https://www.ffmpeg.org/) to run through the preprocessing pipeline. 

## Analysis
This folder contains (1) the Python code we use to generate our model embeddings to use as a measure of similarity between image-pairs and (2) the R code that we use to process the gaze data from iCatcher+, create plots and run our statistical analyses. It also contains the power analysis we conducted to determine the sample size we needed for our study. 

## Data
The data folder contains all levels of data from raw through processed. The raw videos and iCatcher+ processed videos which are inherently identifiable are not shared here. The preprocessed cleaned iCatcher+ and trial-level data, generated from running through `preprocessing/3_process_icatcher_output/main.ipynb`, is in the `data_to_analyze` folders while the processed data, generated during analysis, is in the `processed_data` folders. 

More information on the data to be found in the dataset_description.json file that is being worked on. 

## Running through the pipeline
Since the videos we collected are inherently identifiable (and large) we cannot share them, so we recommend starting at the analysis section if you do not have a set of videos. In general, please install Python packages using the `requirements.txt` file in the main directory to get started. Then, please copy over the `.env_template` file into a `.env` file, filling out the rows as required. Then, refer to the Markdown files in the `preprocessing` and `analysis` subdirectories.

1. Downloading the video ZIP and trial JSON files from Children Helping Science. We used `unzip` to unzip the videos after placing it in `data/original_videos/webm` and placed the trial JSON file as `data/lookit/all_study_data.json` 
2. Running `preprocessing/1_preprocess_raw_data.py` and then `preprocessing/2_run_icatcher/run_icatcher_job_array.sh` (more info soon to be found in sub-directory markdown) to first format the raw videos and clean the Lookit JSON file, and then to run iCatcher+ on all of these  formatted videos.
3. After iCatcher+ has finished running, running `preprocessing/3_process_icatcher_output/main.ipnyb` to process the iCatcher+ data into a single CSV file.
4. Running `analysis/embeddings/main.py` to generate our embedding similarities.
5. Running the Quarto files in `analysis` in the order that they are numbered.