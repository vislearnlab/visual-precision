### Data Storage

Paths are abbreviated: `LOCAL_DIR` is your local machine, `SERVER_DIR` is the polygon server

## Part 1 — Move raw videos and process Lookit JSON

Level 1 · Move raw video and conversion:

```
LOCAL_DIR/raw/raw_videos/*
        │ upload
        ▼
SERVER_DIR/data/raw/original_videos/webm/*
        │ convert 
        ▼
SERVER_DIR/data/raw/original_videos/mp4_converted/*
```

Level 2 · Lookit JSON → trials CSV:

```
SERVER_DIR/data/raw/lookit/sample#/input_lookit.json
        │ clean & format
        ▼
SERVER_DIR/data/main/data_to_analyze/level-trials_source-lookit_data.csv
```

## Part 2 — Run iCatcher+ over converted videos

```
SERVER_DIR/data/raw/original_videos/mp4_converted/*
        │ iCatcher+
        ├──────►  SERVER_DIR/data/raw/icatcher_videos/*
        │
        └──────►  SERVER_DIR/data/raw/icatcher_annotations/*
```

## Part 3 — Process iCatcher output into looks CSV

```
SERVER_DIR/data/raw/icatcher_annotations/*
        │ process (through jupyter notebook)
        ▼
SERVER_DIR/data/main/data_to_analyze/level-looks_source-icatcher_data.csv
```

## Part 4 - WIP


### Local Repo Structure
visual-precision/
├── analysis/             # Part 4 analysis and model similarities
├── data/
│   ├── embeddings/       # embeddings for current sample
│   ├── main/             # local copies of processed iCatcher and Lookit data
│   ├── metadata/
│   ├── pilot/            # pilot data
│   └── raw/              # videos placed in part 1
├── experiment/           # image pairs used
├── figures/              # final-stage graphs for publication
├── models/               # model information
├── preprocessing/        # primary preprocessing scripts
├── stimuli/
├── writing/
├── .env_template
├── .gitignore
├── preprocess.py         # Part 1
├── README.md
└── requirements.txt

### Server Repo Structure
visual-precision/
├── analysis/                       # R scripts and results
├── data/
│   ├── embeddings/                 # model embedding results
│   ├── main/                       # processed iCatcher and Lookit data (CSVs)
│   ├── metadata/
│   ├── pilot/                      # pilot data and analysis for comparison
│   └── raw/
│       ├── icatcher_annotations/   # frame-by-frame gaze data
│       ├── icatcher_videos/        # videos with gaze overlay
│       ├── lookit/                 # Lookit data from Part 2, giftcard scripts
│       └── original_videos/        # webm and mp4 videos
├── frames/                         # image pairs generated
├── models/                         # model information
├── preprocessing/                  # backup copy of preprocessing scripts
├── stimuli/                        # images used for testing
├── writing/                        # drafts
├── config.py
├── dataset_description.json
├── preprocess.py
├── README.md
└── requirements.txt