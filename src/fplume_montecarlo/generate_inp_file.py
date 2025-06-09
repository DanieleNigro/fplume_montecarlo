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

def generate_inp_file(year, month, day, hour, MER, exit_velocity, template_file, output_dir):
    """
    Inserts perturbed volcanic initial conditions into the 'template_fplume.inp' template
    to generate the .inp file required by FPLUME.

    Each parameter is perturbed assuming a Gaussian distribution with specified
    uncertainties based on literature values:
        - MER: 22.3% uncertainty (Mereu et al., 2022)
        - Exit velocity: std dev = 25 m/s
        - Exit temperature: mean = 1390 K, std dev = 6 K (Giordano et al., 2010)
        - Exit water fraction: mean = 3 wt%, std dev = 0.5 (Giordano et al., 2010)
        - cp: mean = 1300 J/kg·K, std dev = 50 (Minett et al., 1988)
        - c_umbrella: mean = 1.2, std dev = 0.025

    Returns:
        Path to the generated .inp file.
    """
    
    date_prefix = f"{year}_{month}_{day}_{hour}"
    parameters = {
        "MER": {"type": "normal", "mean": MER, "std": 0.223 * MER},                
        "exit_velocity": {"type": "normal", "mean": exit_velocity, "std": 25},      
        "exit_temperature": {"type": "normal", "mean": 1390, "std": 6},             
        "exit_water_fraction": {"type": "normal", "mean": 3, "std": 0.5},           
        "cp": {"type": "normal", "mean": 1300, "std": 50},                          
        "c_umbrella": {"type": "normal", "mean": 1.2, "std": 0.025},                
    }

    with open(template_file, "r") as f:
        template = Template(f.read())

    params = {}
    for key, dist in parameters.items():
        if dist["type"] == "normal":
            # --- Use a truncated gaussian distribution to avoid negative unphisical values
            a = (0 - dist["mean"]) / dist["std"]
            b = (np.inf - dist["mean"]) / dist["std"]
            params[key] = truncnorm.rvs(a, b, loc=dist["mean"], scale=dist["std"])

        elif dist["type"] == "uniform":
            params[key] = np.random.uniform(low=dist["min"], high=dist["max"])

    params.update({"year": year, "month": month, "day": day, "hour": hour})

    rendered = template.render(params)
    output_path = Path(output_dir) / f"{date_prefix}.inp"

    with open(output_path, "w") as f:
        f.write(rendered)

    return output_path