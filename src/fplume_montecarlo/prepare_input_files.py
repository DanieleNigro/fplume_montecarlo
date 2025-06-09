"""
Prepares input files for FPLUME Monte Carlo runs by copying the required `.met` and `.tgsd`
files into the TMP_MONTECARLO_DIR working directory as:
    -{date_prefix}.met
    -{date_prefix}.tgsd

The .inp file will be created later by run_montecarlo.py.

Usage:
    python fplume_montecarlo.prepare_input_files --code <n>
    python fplume_montecarlo.prepare_input_files --all
"""

# ---Import packaged
import argparse
import shutil

# --- Import directories and utilites
from fplume_montecarlo.config import ERUPTIONS_FILE, FPLUME_MET_FILES_DIR, TMP_MONTECARLO_DIR, FPLUME_TEMPLATES_DIR
from fplume_montecarlo.utilities import load_events


def main():
    """
    Main function to prepare the input directories for FPLUME by copying
    template and met files into temporary working folders.
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
        raise ValueError("Please specify --code <int> or --all")
    
    for event in events:
        date_prefix = event['date_prefix']

        # ---Temporary working directory for FPLUME
        dest_dir = TMP_MONTECARLO_DIR
        dest_dir.mkdir(parents=True, exist_ok=True)

        # ---Rename the .tgsd file as {data_prefix}.tgsd and copy into the working directory 
        template_tgsd_file = FPLUME_TEMPLATES_DIR / "template_fplume.tgsd"
        tgsd_file = dest_dir / f"{date_prefix}.tgsd"
        shutil.copy(FPLUME_TEMPLATES_DIR / template_tgsd_file, tgsd_file)

        # ---Copy the .met file in the working directory
        met_file = FPLUME_MET_FILES_DIR / f"{date_prefix}.met"
        if not met_file.exists():
            # ---Check if the .met file exists
            print(f"Missing .met file for event {date_prefix}. Please run create_met_file.py")
            return
        shutil.copy(met_file, dest_dir / met_file.name)
        print(f"Prepared inputs in {dest_dir}")

if __name__ == "__main__":
    main()
