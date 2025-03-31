"""
    File containing implementation logic for MCD - Mel Cepstral Distortion metric

    Inspired by: 
    https://github.com/ttslr/python-MCD
"""

import numpy as np
from modules.constants import _cons_log


def eval_mcd(ref: np.ndarray, gen: np.ndarray) -> float:
    """
    Function to compute MCD on alligned MGC

    Params:
        ref     : reference audio MGC 
        gen     : generated audio MGC
    """
    frames = ref.shape[0]
    z = ref - gen
    s = np.sqrt((z * z).sum(-1)).sum()
    mcd = _cons_log * float(s) / float(frames)

    return mcd