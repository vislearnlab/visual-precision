import importlib
from preprocessing.utils import move_to_polygon
from config import *

# Programmatically import the module using its string path
module_path = "preprocessing.1_preprocess_raw_data"
preprocess_module = importlib.import_module(module_path)
preprocess_raw_data = preprocess_module.preprocess_raw_data

 # if being run on the server, do not move files (already in place); if on local, move to server first
if SERVER_PATH is not None and PROJECT_PATH is not None and SERVER_PATH != PROJECT_PATH:
    move_to_polygon.main()
preprocess_raw_data()
