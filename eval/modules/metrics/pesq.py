"""
File containing implementation of PESQ evaluation metric
https://pypi.org/project/pesq/
"""
from pesq import pesq
import numpy as np

class PesqEvaluationError(Exception):
    """An error has occured during PESQ evaluation"""

def eval_pesq(ref_audio: np.array, gen_audio: np.array, rate: int) -> float:
    """
    Evaluates audios using PESQ method.

    Params:
    ref_audio       : reference audio
    gen_audio       : generated/degraded audio
    rate            : sample rate of both audios
    """
    try:
        # Either pesq or pesq_batch (pesq_batch uses multiple cores)
        return pesq(fs=rate, ref=ref_audio, deg=gen_audio, mode='wb')
    except Exception as e:
        raise PesqEvaluationError