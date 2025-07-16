"""
Processes ERA5 pressure-level dataset for Etna volcanic eruption events
listed in list_eruptions.txt and generates .met meteorological profile files 
used as input for the FPLUME volcanic plume model.

Data is interpolated vertically (every 5 hPa) at the Etna volcano location, and
converted into FPLUME's expected tabular format.
Usage:
    python fplume_montecarlo.create_met_file --code <n>
    python fplume_montecarlo.create_met_file --all
"""

# --- Import packages
import argparse
import pandas as pd
import numpy as np
import xarray as xr
from pathlib import Path

# --- Import Import ERA5 directories, volcanic erupions file
from fplume_montecarlo.config import PROJ_ROOT, ERA5_DIR, FPLUME_MET_FILES_DIR, ERUPTIONS_FILE
from fplume_montecarlo.utilities import load_events,load_config

CONFIG = load_config(PROJ_ROOT / "config.yaml")

def process_era5_data(nc_file):
    """
    Processes ERA5 datasets in NetCDF format to extract meteorological variables at Etna's location
    and interpolates them to 5 hPa vertical resolution.

    Parameters:
        nc_file (str or Path): Path to the ERA5 NetCDF file containing pressure-level data.

    Returns:
        df (pd.DataFrame): A DataFrame containing columns:
            - 'Altitude (km)'
            - 'Density (kg/m³)'
            - 'Pressure (hPa)'
            - 'Temperature (K)'
            - 'Specific Humidity (g/kg)'
            - 'Wind Velocity West->East (m/s)'
            - 'Wind Velocity North->South (m/s)'
    """
    # ---Volcano Coordinates
    VOLCANO = CONFIG["volcano"]  # This is now a Volcano object
    lat_volcano = VOLCANO.latitude
    lon_volcano = VOLCANO.longitude

    # ---Select variables and downscale every 5 hPa
    ds = xr.open_dataset(nc_file)
    ds = ds.sel(latitude=lat_volcano, longitude=lon_volcano, method='nearest')

    downscaled_pressure_levels = np.arange(ds.pressure_level.max(), ds.pressure_level.min(), -5)
    ds_interp = ds.interp(pressure_level=downscaled_pressure_levels)

    pressure_levels = ds_interp.pressure_level.values.flatten()
    temperature = ds_interp.t.values.flatten()
    humidity = ds_interp.q.values.flatten() * 1000              # specific humidity in g/kg
    u_wind = ds_interp.u.values.flatten()
    v_wind = ds_interp.v.values.flatten()
    geopotential = ds_interp.z.values.flatten()
    altitude = geopotential / 9.80665 / 1000                    # altitude in km from geopotential
    density = pressure_levels * 100 / (287.05 * temperature)

    # ---Create DataFrame
    df = pd.DataFrame({
        'Altitude (km)': altitude,
        'Density (kg/m³)': density,
        'Pressure (hPa)': pressure_levels,
        'Temperature (K)': temperature,
        'Specific Humidity (g/kg)': humidity,
        'Wind Velocity West->East (m/s)': u_wind,
        'Wind Velocity North->South (m/s)': v_wind
    })

    return df

def save_to_txt(df, output_file):
    """
    Writes the meteorological DataFrame to a .met file in the tabular format required by FPLUME.

    Args:
        df (pd.DataFrame): DataFrame with processed meteorological data.
        output_file (str or Path): Destination path for the output .met file.

    Returns:
        None
    """
    with open(output_file, 'w') as f:
        f.write("# Z(asl)    Density     Pressure   Temperature   Specific-humidity  Wind-velocity       Wind-velocity\n")
        f.write("#  (km)   (kg/m^3)      (hPa)        (K)          (g/kg)         West->East(m/s)    North->South(m/s)\n")
        df.to_csv(f, sep='\t', index=False, header=False, float_format='%.3f')

def main():
    """
    Entry point for command-line usage. Processes a specific or all eruption events,
    converting ERA5 NetCDF files into .met format for FPLUME.
    """

    parser = argparse.ArgumentParser(description="Create .met file from ERA5 data")
    parser.add_argument("--code", type=int, help="Code of the event to process")
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
        nc_file = f"{ERA5_DIR}/{date_prefix}_pressure_levels.nc"
        output_file = FPLUME_MET_FILES_DIR / f"{date_prefix}.met"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"Processing ERA5 file: {nc_file}")
        df = process_era5_data(nc_file)
        save_to_txt(df, output_file)
        print(f"Saved met file to: {output_file}")

if __name__ == "__main__":
    main()
