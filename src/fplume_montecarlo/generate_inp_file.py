"""
Creates the .inp file containing the volcanological initial parameters.

The file is generated from the template "template_fplume.inp" contained 
in FPLUME_TEMPLATES_DIR. The function explots jinja2.

The parameters are perturbed assuming a gamma distribution perturbation,
using mean and standard deviations from typical values in literature.

The module is used in run_montecarlo.py

Usage:
    python fplume_montecarlo.generate_inp_file --code <n>
    python fplume_montecarlo.generate_inp_file --all
"""

# --- Import packages
import numpy as np
from jinja2 import Template
from scipy.stats import truncnorm
from pathlib import Path
from fplume_montecarlo.utilities import load_config
from fplume_montecarlo.config import PROJ_ROOT

CONFIG = load_config(PROJ_ROOT / "config.yaml")

def generate_inp_file(year, month, day, hour, MER, exit_velocity, template_file, output_dir):
    """
    Inserts perturbed volcanic initial conditions into the 'template_fplume.inp' template
    to generate the .inp file required by FPLUME.

    Each parameter is perturbed assuming a Gaussian distribution. Default values with specified
    uncertainties are based on literature values for Etna:
        - MER: 22.3% uncertainty (Mereu et al., 2022)
        - Exit velocity: std dev = 25 m/s
        - Exit temperature: mean = 1390 K, std dev = 6 K (Giordano et al., 2010)
        - Exit water fraction: mean = 3 wt%, std dev = 0.5 (Giordano et al., 2010)
        - cp: mean = 1300 J/kg·K, std dev = 50 (Minett et al., 1988)
        - c_umbrella: mean = 1.2, std dev = 0.025

    The user can modify these value in config.yaml.

    Returns:
        Path to the generated .inp file.
    """

    param_montecarlo = CONFIG["parameters_montecarlo"]
    
    parameters = {}
    for name, settings in param_montecarlo.items():
        if settings["mean"] == "MER":
            mean = MER
            std = settings["std_factor"] * MER
        elif settings["mean"] == "exit_velocity":
            mean = exit_velocity
            std = settings["std"]
        else:
            mean = settings["mean"]
            std = settings["std"]

        parameters[name] = {
            "mean": mean,
            "std": std
        }

    with open(template_file, "r") as f:
        template = Template(f.read())

    # --- Sample parameter values using truncated normal to avoid negative unphisical values
    sampled_params = {}
    for name, stats in parameters.items():
        mean, std = stats["mean"], stats["std"]
        a = (0 - mean) / std
        b = (np.inf - mean) / std
        sampled_params[name] = truncnorm.rvs(a, b, loc=mean, scale=std)

    # --- Add date/time for the template
    sampled_params.update({"year": year, "month": month, "day": day, "hour": hour})

    # --- Render template
    rendered = template.render(sampled_params)

    # --- Write .inp file
    date_prefix = f"{year}_{month}_{day}_{hour}"
    output_path = Path(output_dir) / f"{date_prefix}.inp"

    with open(output_path, "w") as f:
        f.write(rendered)

    return output_path