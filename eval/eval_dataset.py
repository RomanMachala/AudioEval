"""
This file contains main body for evaluation script of synhtesized audio.
This script was created as a part of Bachelor's thesis of
Roman Mahala at VUT Brno.
"""

__author__  = "Roman Machala"
__date__    = "14.12.2024"
__version__ = "0.1"

import numpy as np
from scipy.io import wavfile
import librosa
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import pysptk
import os
from metrics.pesq import eval_pesq, PesqEvaluationError
from metrics.stoi import eval_stoi, eval_estoi, StoiEvaluationError
from metrics.mcd import eval_mcd
from speechmos import dnsmos

class InvalidMetaFileValue(Exception):
    """Meta file contains an invalid value, skipping current line"""
    pass

class InvalidFrameLength(Exception):
    """Current audio couldn't be evaluated due to invalid frame length"""
    pass

class ResampleError(Exception):
    """Selected audio couldn't be resampled to desired sample rate"""
    pass

class MGCCalculationError(Exception):
    """An error has occured during MGC calculation"""
    pass

class Audio:
    """
    A class representing audio
    """
    def __init__(self, filename: str):
        self.filename = filename
        self.rate, self.audio = wavfile.read(filename)

    def resample(self, new_sr) -> np.ndarray:
        """
        A method for resampling original audio 
        in case some methods explicitly needs a specific sample rate

        Args:
            new_sr      : new sample rate
        """
        return librosa.resample(
            y=self.audio.astype(np.float64),
            orig_sr=self.rate,
            target_sr=new_sr
        )
    
    def normalize(self) -> np.ndarray:
        """
            Method for normalization.
            wavfile reads file as ints or floats, dnsmos
            expects values in a range from -1 to 1.

            Returns:
                normalized np.array
        """
        if self.audio.dtype == np.int16:
            return self.audio.astype(np.float32) / 32768.0
        elif self.audio.dtype == np.int32:
            return self.audio.astype(np.float32) / 2147483648.0
        elif self.audio.dtype == np.uint8:
            return (self.audio.astype(np.float32) - 128) / 128.0
        else:
            return self.audio.astype(np.float32)

    def extract_mgc(self, frame_length=512, hop_length=128, order=24, alpha=0.35, stage=5):
        """
            MGC extraction method.

            Params:
                frame_length:       lenght of frame
                hop_length:         move length
                order:              --
                alpha:              --
                stage:              --

            Returns:
                MGC coefficients
        """
        # If invalid sample rate, resample
        if self.rate != 16000:
            try:
                x = self.resample(16000)
            except Exception as e:
                raise ResampleError
        else:
            x = self.audio 
        
        x = x.astype(np.float64)

        frames = librosa.util.frame(x, frame_length=frame_length, hop_length=hop_length).astype(np.float64).T
        frames *= pysptk.blackman(frame_length)
        if frames.shape[1] != frame_length:
            raise InvalidFrameLength

        gamma = -1.0 / stage

        try:
            mgc = pysptk.mgcep(frames, order, alpha, gamma)
        except RuntimeError as e:
            raise MGCCalculationError

        return mgc.reshape(-1, order + 1)

def get_audios(line: str, dataset_path: str) -> list[Audio]:
    """
    Function to get reference and gen audio from meta file line

    Params:
        line            : one line from meta file
        dataset_path    : in case paths in meta file are relative

    Returns:
        reference and generated audios
    """
    file_paths = line.strip().split()
    # If line in meta file doesnt contain 2 files, raise an exception
    if(len(file_paths) != 2):
        raise InvalidMetaFileValue
    
    if dataset_path:
        return [Audio(os.path.join(
                    dataset_path,
                    file_paths[0]
                )),
                Audio(os.path.join(
                    dataset_path,
                    file_paths[1]
                ))
                ]
    
    # Returns audios as correct paths
    return [Audio(file_paths[0], Audio(file_paths[1]))]

def eval_audio(ref_audio: Audio, gen_audio: Audio):
    """
    Evaluates audios. 

    Params:
        ref_audio       : reference audio
        gen_audio       : generated audio

    This function uses 2 step evaluation:
    First:
        MGC coefficients are extracted
        MGC are alligned using DTW
        Alligned MGC are used for MCD evaluation
        (More fleible and better results compared to MFCC)
    Second:
        Raw audio signals are converted to 2D
        These signals are aligned using DTW
        Aligned signals are evaluated using methods 
            requiring aligned, same length signals
            (PESQ, STOI, ESTOI, ...)
    
    Such approach is needed for the best results. Could also
    convert alligned MGC back to signals, but that would require 
    a vocoder -> synthesis.

    """
    # MGC extraction for MCD evaluation
    try:
        ref_mgc1 = ref_audio.extract_mgc()
        gen_mgc2 = gen_audio.extract_mgc()
    except ResampleError as e:
        print("Error resampling")
        raise e
    except InvalidFrameLength as e:
        print("error frame lenght")
        raise e
    except MGCCalculationError as e:
        print("Error MGC")
        raise e
    #TODO handle exceptions

    # FOR PESQ, STOI and ESTOI evaluation
    ref_audio_2d = ref_audio.audio.reshape(-1, 1)
    gen_audio_2d = gen_audio.audio.reshape(-1, 1)
    # dynamic time warping based on MGC 
    distance, path = fastdtw(ref_mgc1, gen_mgc2, dist=euclidean)
    distance /= (len(ref_mgc1) + len(gen_mgc2))

    path_ref = list(map(lambda l: l[0], path))
    path_gen = list(map(lambda l: l[1], path))
    # Dynamic time warping on raw audios
    distance, path = fastdtw(ref_audio_2d, gen_audio_2d, dist=euclidean)
    ref_1d = np.array([ref_audio.audio[p[0]] for p in path])
    gen_1d = np.array([gen_audio.audio[p[1]] for p in path])
    ref, gen = ref_mgc1[path_ref], gen_mgc2[path_gen]
    #ref, gen contains alligned audios
    
    # Alligned MGC are used for MCD evaluation
    try:
        mcd = eval_mcd(ref=ref, gen=gen)
    except Exception as e:
        mcd = "NaN"
    # Raw signals alligned are used for PESQ, STOI and ESTOI evaluation
    try:
        pesq = eval_pesq(ref_audio=ref_1d, gen_audio=gen_1d, rate=ref_audio.rate)
    except PesqEvaluationError as e:
        pesq = "NaN"
    try:
        stoi = eval_stoi(ref_audio=ref_1d, gen_audio=gen_1d, rate=ref_audio.rate)
    except StoiEvaluationError as e:
        stoi = "NaN"
    try:
        estoi = eval_estoi(ref_audio=ref_1d, gen_audio=gen_1d, rate=ref_audio.rate)
    except StoiEvaluationError as e:
        estoi = "NaN"
    try:
        mos = dnsmos.run(gen_audio.normalize(), 16000)
    except Exception as e:
        print(e)
        mos = "NaN"

    print (mcd, pesq, stoi, estoi, mos)
    return mcd, pesq, stoi, estoi, mos
    #TODO handle exceptions