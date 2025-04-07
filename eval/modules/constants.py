"""
    this file contains constants used in the aduio evaluation system.
"""
import numpy as np

RESULTS_FILE    = "results.json"
GRAPHS_PATH     = 'static/graphs'
UPLOAD_PATH     = 'uploads'
SAMPLES_PATH    = 'static/samples'
NUM_OF_SAMPLES = 5

# Genral structure of response for visualization
# Automatically adds new metrics based on provided json file
# If you want to remove any metrics - just remove the function for it's call
# and finally remove all mentions of this function below to not display empty sections in web
PLOTS_RESULT = {
    "plots":{
        "Pesq": [],
        "Stoi": [],
        "Estoi": [],
        "Mcd": [],
        "Mos": []
    },
    "tables": {
        "Files": [],
        "Values": {
            "Pesq": [],
            "Stoi" : [],
            "Estoi": [],
            "Mcd": [],
            "ovrl_mos": [],
            "sig_mos" : [],
            "bak_mos": [],
            "p808_mos": []
        }
    },
}