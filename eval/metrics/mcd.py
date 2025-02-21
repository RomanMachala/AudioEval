import numpy as np

_cons_log = 10.0 / np.log(10.0) * np.sqrt(2.0)
# Constant used in MCD equation

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