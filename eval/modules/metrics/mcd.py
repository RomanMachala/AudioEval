"""
    Mel-Cepstral Distortion metric
    Original work: 
    https://github.com/jasminsternkopf/mel_cepstral_distance
"""
from mel_cepstral_distance import compare_audio_files

def eval_mcd(ref: str, gen: str) -> float:
    """
        Evaluates audios using mel-cepstral-distortion metric

        Params:
            ref:            reference audio path
            gen:            generated audio path

        Returns:
            MCD value in dB
    """
    mcd, _ = compare_audio_files(ref, gen)

    return mcd