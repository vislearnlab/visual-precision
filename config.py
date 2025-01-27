import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Project paths
PROJECT_PATH = os.environ.get("PROJECT_PATH")
SERVER_PATH = os.environ.get("SERVER_PATH", PROJECT_PATH)

# Project version
PROJECT_VERSION = os.environ.get("PROJECT_VERSION")
PROJECT_VERSION = PROJECT_VERSION.lower() if PROJECT_VERSION is not None else "pilot" 
