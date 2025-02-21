"""
Implementation of STOI and ESTOI evaluation metrics
https://github.com/mpariente/pystoi
"""
from pystoi import stoi
import numpy as np

class StoiEvaluationError(Exception):
    """An error has occured during STOI/ESTOI evaluation"""
    pass

def eval_stoi(ref_audio: np.ndarray, gen_audio: np.ndarray, rate: int) -> float:
    """
    Evaluates audios using STOI method.

    Params:
    ref_audio       : reference audio
    gen_audio       : generated/degraded audio
    rate            : sample rate of both audios
    """
    try:
        return stoi(ref_audio, gen_audio, rate, extended = False)
    except Exception as e:
        raise StoiEvaluationError
    
def eval_estoi(ref_audio: np.ndarray, gen_audio: np.ndarray, rate: int) -> float:
    """
    Evaluates audios using ESTOI method

    Params:
    ref_audio       : reference audio
    gen_audio       : generated/degraded audio
    rate            : sample rate of both audios
    """
    try:
        return stoi(ref_audio, gen_audio, rate, extended = True)
    except Exception as e:
        raise StoiEvaluationError