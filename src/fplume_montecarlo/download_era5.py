"""
Downloads ERA5 reanalysis data (pressure levels) in NetCDF format
for the volcanic eruption events contained in list_eruptions.txt.

Data is retrieved using the Copernicus Climate Data Store (CDS) API.

Usage:
    python fplume_montecarlo.download_era5 --code <n>
    python fplume_montecarlo.download_era5 --all
"""
# --- Import packages
import cdsapi
import os
import argparse

# --- Import ERA5 directories, volcanic erupions file, and ERA5 key API file from local
from fplume_montecarlo.config import ERUPTIONS_FILE, ERA5_DIR, KEYS_DIR, KEY_ERA5_FILE

# --- Import progress bar function
from fplume_montecarlo.utilities import progress_bar, load_events

# --- Import Copernicus ERA5 API from local
CDS_URL = 'https://cds.climate.copernicus.eu/api'

with open(os.path.join(KEYS_DIR,KEY_ERA5_FILE)) as f:
    CDS_KEY = f.read().strip()

# --- Select variables to download from the pressure level dataset
pressure_level_vars = [
    "geopotential", "potential_vorticity", "relative_humidity", "specific_humidity",
    "temperature", "u_component_of_wind", "v_component_of_wind", "vertical_velocity","divergence"
    ]

# --- Select pressure levels to download
pressure_levels=["5", "7", "10", "20", "30",
    "50", "70", "100","125", "150", "175",
    "200", "225", "250","300", "350", "400",
    "450", "500", "550","600", "650", "700",
    "750", "775", "800","825", "850", "875",
    "900", "925", "950","975", "1000",
]
# --- Select domain to download  [N W S E]
area = [38, 14, 36, 16]   # reasonable domain for Etna location: lat = 37.75, lon = 15.00


def download_era5_pressure_levels(year, month, day, hour, pressure_level_vars, pressure_levels, CDS_URL, CDS_KEY):
    """
    Download ERA5 pressure-level data for Etna's eruptions events (from list).
    The downloaded NetCDF file is saved locally in the ERA5_DIR directory with a filename based on the date.

    Parameters:
        year (str): year of the event in "YYYY" format;
        month (int): month of the event in "MM" format;
        day (int): day of the event in "DD" format;
        hour (int): hour of the event in "HH:MM" format;
        pressure_level_vars (list of str): ERA5 variable names to download;
        pressure_levels (list of str): pressure levels (in hPa) to include in the dataset;
        CDS_URL (str): URL for the Copernicus Climate Data Store API;
        CDS_KEY (str): API key for authenticating with the CDS.

    Returns:
        None. Saves the data to a NetCDF file in ERA5_DIR.
    """
    c = cdsapi.Client(url=CDS_URL, key=CDS_KEY)

    # ---Download pressure-level data
    if pressure_level_vars and pressure_levels:
        request_params_pressure = {
            "product_type": ["reanalysis"],
            "variable": pressure_level_vars,
            "year": [int(year)],
            "month": [int(month)],
            "day": [int(day)],
            "time": [f"{int(hour):02d}:00"],
            "pressure_level": pressure_levels,
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": area
        }
        date_prefix = f"{year}_{month}_{day}_{hour}"
        filename_pressure = f"{ERA5_DIR}/{date_prefix}_pressure_levels.nc"

        print(f"Starting download of pressure level data for {filename_pressure}")
        
        response = c.retrieve('reanalysis-era5-pressure-levels', request_params_pressure)
        download_url = response.location

        # ---Show progress bar while downloading
        progress_bar(download_url, filename_pressure)
        print(f"Pressure level data saved as {filename_pressure}")

# ---Main execution loop
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Download ERA5 pressure level data for eruption events.")
    parser.add_argument("--code", type=int, help="Event code to download (from eruption file)")
    parser.add_argument("--all", action="store_true", help="Download all events")
    args = parser.parse_args()

    if args.all:
        events = load_events(ERUPTIONS_FILE)
        for event in events:
            download_era5_pressure_levels(
                event["year"], event["month"], event["day"], event["hour"], pressure_level_vars, pressure_levels, CDS_URL, CDS_KEY
                )
    elif args.code is not None:
        event = load_events(ERUPTIONS_FILE, code=args.code)
        download_era5_pressure_levels(
            event["year"], event["month"], event["day"], event["hour"], pressure_level_vars, pressure_levels, CDS_URL, CDS_KEY
            )
    else:
        raise ValueError("Please specify either --code <int> or --all.")