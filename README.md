# fplume_montecarlo

This repository performs a Monte Carlo simulation to estimate the height of Etna's volcanic clouds using FPLUME. Meteorological input data are retrieved from ERA5 reanalysis, and the Mass Eruption Rate (MER) is derived from weather radar observations. The distribution of of simulated plume heights is then compared to radar measurements.

## Project structure

The project structure is adapted from the cookiecutter data-science template:
https://cookiecutter-data-science.drivendata.org/
```
├── Makefile                                            # Makefile with convenience commands like `make data` or `make train`
├── README.md                                           # This README
├── config.yaml                                         # Configuration file
├── bin                                                 # Executables
│   └── run_montecarlo.sh                               # Run the full workflow
├── data                                                
│   ├── external                                        # Data from third party sources
│   │   └── ERA5                                        # Downloaded ERA5 reanalysis files
│   ├── interim                                         # Intermediate data that has been transformed
│   │   ├── met_files                                   # Generated .met files for FPLUME
│   │   ├── templates                                   # Input templates for FPLUME
│   │   │   ├── template_fplume.inp                     # Volcanic parameters input template
│   │   │   └── template_fplume.tgsd                    # Particle size distribution input template
│   │   └── tmp_montecarlo                              # Temporary working directory for FPLUME runs
│   ├── processed                                       # Final, processed data
│   │   └── column_files                                # Simulation outputs of plume height
│   │  
│   └── raw                                             # Original data
│       └── list_eruptions.txt                          # List of eruption events to process
├── plots                                               # Output figures
├── pyproject.toml                                      # Project configuration file with package metadata
├── requirements.txt                                    # Python dependencies
└── src                                                
    └── fplume_montecarlo                               
        ├── __init__.py                                 
        ├── config.py                                   # Global configuration and constants
        ├── volcanoes.py                                # Define the class volcano
        ├── create_met_file.py                          # Generate .met file from ERA5 reanalysis
        ├── download_era5.py                            # Download ERA5 datasets
        ├── generate_inp_file.py                        # Generate .inp file for FPLUME
        ├── plot_montecarlo.py                          # Plot Monte Carlo results
        ├── prepare_input_files.py                      # Prepare inputs for FPLUME runs
        ├── run_montecarlo.py                           # Run Monte Carlo Simulation
        ├── qqplot_montecarlo.py                        # Create qq plots from Monte Carlo results
        └── utilities.py                                # Helper functions
```
## Requirements

1. **Install FPLUME v1.3**

FPLUME requires a Linux environment, and GFortran version <= 8 (available in Ubuntu versions <= 20). Download FPLUME v1.3 from this site: http://datasim.ov.ingv.it/models/fplume.html and follow the instructions of the user manual to install. The software must be installed in the root directory of the project, and the folder must be named "fplume-1.3".

2. **Copernicus CDS Account** 

To donload ERA5 reanalysis, please register to the site: https://cds.climate.copernicus.eu/. Copy your API key from your CDS profile and save locally in a .txt file. Then modify KEYS_DIR and KEY_ERA5_FILE to point to your file.

3. **Create and activate a virtual environment**

In the project root:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## Workflow
1. **Add eruption events**

Edit list_eruptions.txt. For each event, specify an integer code, year (YYYY), month (MM), day (DD) and hour (HH) of the eruptions. Add the Mass Eruption Rate (kg/s) retrieved from the weather radar, the exit velocity (m/s), and the height of the volcanic column retrieved from the weather radar.

2. **Configure simulation**

Edit config.yaml, selecticing the Volcano, the number of Monte Carlo iterations and the range of input parameters for F>

3. **Download ERA5 pressure-levels datasets**
```
python -m fplume_montecarlo.download_era5 --code <int>         # for a single event
python -m fplume_montecarlo.download_era5 --all                # for all the events
```
4. **Create the .met file from ERA5 datasets**

These files contain the vertical profile of meteorological variables required by FPLUME:
```
python -m fplume_montecarlo.create_met_file --code <int>         # for a single event
python -m fplume_montecarlo.create_met_file --all                # for all the events
```
5. **Prepare input files for FPLUME** 

Copies the required .met file and the .tgsd file (containing the particle size distribution) to the working directory. The .tgsd file is fixed by default for all the events, while the .met file is stationary throught the Monte Carlo simulation.
```
python -m fplume_montecarlo.prepare_input_files --code <int>         # for a single event
python -m fplume_montecarlo.prepare_input_files --all                # for all the events
```
6. **Run the Monte Carlo simulation** 

For each iteration, a .inp file (from template_fplume.inp) containing the perturbed volcanic initial conditions, is generated and used by FPLUME. The resulting plume height is stored in .column files. The number of iterations is set by N_MONTECARLO in config.py
```
python -m fplume_montecarlo.run_montecarlo --code <int>         # for a single event
python -m fplume_montecarlo.run_montecarlo --all                # for all the events
```
7. **Plot results**

Generate a three-panel figure:
-top: boxplots of simulated column heights and scatter plot of radar observations;
-center: ECDF of the radar column height within the distribution simulation;
-bottom: MER bar chart of all the events.
```
python -m fplume_montecarlo.plot_montecarlo
python -m fplume_montecarlo.qqplot_montecarlo
```
## Run all with bash script

To automate the workflow:
```
./run_montecarlo.sh --code <int>                                # for a single event
./run_montecarlo.sh --all                                       # for all the events
```
This script:
- Activates the virtual environment;
- Sets the correct paths;
- Executes the entire workflow in sequence.
