#!/bin/bash

# Exit if one command fails

set -e  

# Go to the project root directory

cd ..

# Activate python virtual environment

source venv/bin/activate

# Go in the src directory

cd src

# Check if any argument is given
if [ $# -eq 0 ]; then
  echo "Usage: $0 --code <n> OR $0 --all"
  exit 1
fi

# Parse arguments
if [ "$1" == "--all" ]; then
  python -m fplume_montecarlo.download_era5 --all
  python -m fplume_montecarlo.create_met_file --all
  python -m fplume_montecarlo.prepare_input_files --all
  python -m fplume_montecarlo.run_montecarlo --all
  python -m fplume_montecarlo.plot_montecarlo
  python -m fplume_montecarlo.qqplot_montecarlo
elif [ "$1" == "--code" ]; then
  if [ -z "$2" ]; then
    echo "Error: Missing number after --code"
    echo "Usage: $0 --code <n>"
    exit 1
  fi
  python -m fplume_montecarlo.download_era5 --code $2
  python -m fplume_montecarlo.create_met_file --code $2
  python -m fplume_montecarlo.prepare_input_files --code $2
  python -m fplume_montecarlo.run_montecarlo --code $2
  python -m fplume_montecarlo.plot_montecarlo
  python -m fplume_montecarlo.qqplot_montecarlo
else
  echo "Invalid option: $1"
  echo "Usage: $0 --code <n> OR $0 --all"
  exit 1
fi
deactivate
