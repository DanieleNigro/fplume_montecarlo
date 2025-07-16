"""
Runs FPLUME for a number of steps defined by n_montecarlo to simulate 
the volcanic column height.

Generates a .column file containing the distribution of simulated column heights.

Usage:
    python fplume_montecarlo.run_montecarlo --code <n>
    python fplume_montecarlo.run_montecarlo --all
"""

# ---Import packages
import subprocess
import argparse
import shutil

# ---Import directories and utilities
from fplume_montecarlo.generate_inp_file import generate_inp_file
from fplume_montecarlo.config import PROJ_ROOT, ERUPTIONS_FILE, FPLUME_EXE_DIR, TMP_MONTECARLO_DIR, TEMPLATE_FILE, COLUMN_FILES_DIR
from fplume_montecarlo.utilities import load_events, load_config

CONFIG = load_config(PROJ_ROOT / "config.yaml")

# ---Load n_montecarlo from config.yaml

n_montecarlo = CONFIG["n_montecarlo"]

# ---FPLUME executable file
FPLUME_EXE = FPLUME_EXE_DIR / "fplume"

def run_fplume(event):
    """
    Runs the FPLUME executable for a single eruption event using Monte Carlo sampling.


    The simulation requires the following input files:
        - .met file: meteorological profile at the Etna location.
        - .tgsd file: particle size distribution (PSD) for a typical eruption.
        - .inp file: initial volcanic conditions (perturbed for each Monte Carlo iteration).
    """ 

    date_prefix = event["date_prefix"]
    output_dir = TMP_MONTECARLO_DIR

    # ---Initialize .column file
    column_file = output_dir / f"{date_prefix}.column"
    column_file.unlink(missing_ok=True)  # Remove if it exists

    for i in range(1, n_montecarlo +1):
        print(f"  Iteration {i} of {n_montecarlo} for {date_prefix}")

        # ---Generate randomized input file
        inp_path = generate_inp_file(
            event["year"], event["month"], event["day"], event["hour"],
            event["mer"], event["exit_v"],
            TEMPLATE_FILE,
            output_dir
        )
        
        target_path = FPLUME_EXE_DIR / "tmp_montecarlo"
        target_path.mkdir(parents=True, exist_ok=True)

        # ---Copy .met, .tgsd, .inp files in the working directory
        for item in output_dir.iterdir():
            if item.is_file():
                shutil.copy(item, target_path)


        # ---Run FPLUME
        a = 'fplume'
        b = f'tmp_montecarlo/{date_prefix}'
        subprocess.run([str(a), str(b)],check=True,cwd=str(FPLUME_EXE_DIR))

        # ---Read result file containing the outputs of the FPLUME run and retrieve the column height
        result_file = target_path / f"{date_prefix}.01.res"
        if not result_file.exists():
            raise FileNotFoundError(f"{result_file} not found")

        with open(result_file, "r") as f:
            lines = f.readlines()
        if lines:
            last_val = lines[-1].split()[0]
            with open(column_file, "a") as col_f:
                col_f.write(last_val + "\n")

        # ---Clear working directories        
        if i == n_montecarlo:
            shutil.copy(column_file, COLUMN_FILES_DIR)

            # Clean only files/directories starting with date_prefix inside target_path
            for item in target_path.iterdir():
                if item.name.startswith(date_prefix):
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

            # Similarly, clean only matching files/directories in TMP_MONTECARLO_DIR
            for item in TMP_MONTECARLO_DIR.iterdir():
                if item.name.startswith(date_prefix):
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

def main():
    """
    Parses command-line arguments and runs FPLUME for specified eruption events.
    """
    parser = argparse.ArgumentParser(description="Prepare FPLUME input folders")
    parser.add_argument("--code", type=int, help="Process only one event by code")
    parser.add_argument("--all", action="store_true", help="Process all events")
    args = parser.parse_args()

    if args.all:
        events = load_events(ERUPTIONS_FILE, code=None)
    elif args.code:
        events = [load_events(ERUPTIONS_FILE, code=args.code)]
    else:
        raise ValueError("Please specify --code <int>")
    
    for event in events:
        date_prefix = event['date_prefix']
        print(f"Processing event {date_prefix}")
        run_fplume(event)

if __name__ == "__main__":
    main()
