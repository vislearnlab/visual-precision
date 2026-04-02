from preprocessing.preprocess_raw_data_1 import preprocess_raw_data
from preprocessing.utils import move_to_polygon
from config import *

 # if being run on the server, do not move files (already in place); if on local, move to server first
if SERVER_PATH is not None and PROJECT_PATH is not None and SERVER_PATH != PROJECT_PATH:
    move_to_polygon.main()
preprocess_raw_data()
