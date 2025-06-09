"""
Initialize paths and global variables.

IMPORTANT:
- Modify "KEYS_DIR" to point to your local path containing the Copernicus CDS API key;
- Adjust N_MONTECARLO based on your analysis
"""

# ---Import packages

from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Simulation settings
N_MONTECARLO = 100                               # Number of Monte Carlo simulations to run (adjust as needed for your analysis)

# --- API Keys directory (user-specific)
KEYS_DIR = '/home/danie/keys'                    # <- Replace with your local path to the Copernicus API key file
KEY_ERA5_FILE = 'copernicus_era5_key.txt'        # <- Replace with your file containing the Copernicus API key

# --- Root directory
PROJ_ROOT = Path(__file__).resolve().parents[2]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

# --- PATHS

# --- Standardized data directory
DATA_DIR = PROJ_ROOT / "data"

# --- Raw unprocessed data directory
RAW_DATA_DIR = DATA_DIR / "raw"                              # Parent directory

# --- Volcanic eruption events directory
ERUPTIONS_DIR = RAW_DATA_DIR                                 # Parent directory
ERUPTIONS_FILE = ERUPTIONS_DIR / "list_eruptions.txt"        # txt file containing the list of the volcanic eruptions 

# --- Intermediate data directories
INTERIM_DATA_DIR = DATA_DIR / "interim"                      # Parent directory
FPLUME_MET_FILES_DIR = INTERIM_DATA_DIR / "met_files"        # met files directory
TMP_MONTECARLO_DIR = INTERIM_DATA_DIR / "tmp_montecarlo"     # Temporary directory for FPLUME input files
FPLUME_TEMPLATES_DIR = INTERIM_DATA_DIR / "templates"        # Contains .inp and .tgsd templates for FPLUME
TEMPLATE_FILE = FPLUME_TEMPLATES_DIR / "template_fplume.inp" # Template file for volcanological input variables

# --- Processed data directories
PROCESSED_DATA_DIR = DATA_DIR / "processed"                  # Parent directory
COLUMN_FILES_DIR = PROCESSED_DATA_DIR / "column_files"       # Contains .column files from Montecarlo simulations

# --- External data directiories
EXTERNAL_DATA_DIR = DATA_DIR / "external"                    # Parent directory
ERA5_DIR = f'{EXTERNAL_DATA_DIR}/ERA5'                       # Contains ERA5 dataset downloaded from download_era5.py

# --- Plots directory
PLOTS_DIR = PROJ_ROOT / "plots"                              # Parent directory

# --- FPLUME executable directory (download from FPLUME v1.3 from http://datasim.ov.ingv.it/models/fplume.html)
FPLUME_EXE_DIR = PROJ_ROOT / "fplume-1.3/src"

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
