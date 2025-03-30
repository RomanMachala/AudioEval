import numpy as np

_cons_log = 10.0 / np.log(10.0) * np.sqrt(2.0)
RESULTS_FILE    = "results.json"
GRAPHS_PATH     = 'static/graphs'
UPLOAD_PATH     = 'uploads'

PLOTS_RESULT = {
    "Pesq": [],
    "Stoi": [],
    "Estoi": [],
    "Mcd": [],
    "Mos": [],
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

USED_METRICS = ['Pesq', 'Stoi', 'Estoi', 'Mcd', 'Mos']
