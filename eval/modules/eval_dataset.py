"""
This file contains main body for evaluation script of synhtesized audio.
This script was created as a part of Bachelor's thesis of
Roman Mahala at VUT Brno.
"""

__author__      = "Roman Machala"
__date__        = "14.12.2024"
__version__     = "0.1"

import numpy as np
from scipy.io import wavfile
import librosa
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import os
from modules.metrics.pesq import eval_pesq, PesqEvaluationError
from modules.metrics.stoi import eval_stoi, eval_estoi, StoiEvaluationError
from modules.metrics.mcd import eval_mcd
from speechmos import dnsmos
from modules.constants import RESULTS_FILE, UPLOAD_PATH, SAMPLES_PATH
import concurrent.futures
from speechmos import dnsmos
from modules.handlers.log_handler import log_event, save_results, convert
from modules.handlers.file_handler import delete_temp_files
from modules.handlers.samples_handler import load_audios

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
        raise InvalidMetaFileValue("Invalid line in meta file - couldn't load both: reference and generated sample.")
    
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
    Evaluates audios using predetermined set of evaluation metrics

    Params:
        ref_audio       : reference audio
        gen_audio       : generated audio
    
    Returns: 
        a set of values
    """
    if ref_audio.rate != 16000:
        temp_ref = ref_audio.resample(16000)
    else:
        temp_ref = ref_audio.audio
    if gen_audio.rate != 16000:
        temp_gen = gen_audio.resample(16000)
    else:
        temp_gen = gen_audio.audio
    # FOR PESQ, STOI and ESTOI evaluation
    ref_audio_2d = temp_ref.reshape(-1, 1)
    gen_audio_2d = temp_gen.reshape(-1, 1)

    # Dynamic time warping on raw audios
    distance, path = fastdtw(ref_audio_2d, gen_audio_2d, dist=euclidean)
    ref_1d = np.array([temp_ref[p[0]] for p in path])
    gen_1d = np.array([temp_gen[p[1]] for p in path])

    #ref, gen contains alligned audios
    
    # Alligned MGC are used for MCD evaluation
    try:
        mcd = eval_mcd(ref=ref_audio.filename, gen=gen_audio.filename)
    except Exception as e:
        mcd = "NaN"
    # Raw signals alligned are used for PESQ, STOI and ESTOI evaluation
    try:
        pesq = eval_pesq(ref_audio=ref_1d, gen_audio=gen_1d, rate=16000)
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
        mos = "NaN"

    return mcd, pesq, stoi, estoi, mos

def process_line(line: str, dataset_path: str, web_mode: bool, intrusive: bool = False):
    """
        Function to evaluate audios specificated by line in meta file

        Params:
            line:           contains ref and gen audio path
            dataset_path:   path to dataset
            web_mode:       logging mode
            intrusive:      whether to assess audios using intrusive methods

        Returns:
            results of evaluation
    """
    try:
        # Gets reference and generated audio
        if intrusive:
            try:
                ref_audio, gen_audio = get_audios(line=line, dataset_path=dataset_path)
            except InvalidMetaFileValue as e:
                raise e
            # Gets evaluation
            mcd, pesq, stoi, estoi, mos = eval_audio(ref_audio=ref_audio, gen_audio=gen_audio)
        else:
            if " " in line:
                audio_path = line.strip().split(" ")[1]
            else:
                audio_path = line.strip()
            gen_audio = Audio(audio_path if dataset_path is None else os.path.join(dataset_path, audio_path))
            mos = dnsmos.run(gen_audio.normalize(), 16000)
            mcd, pesq, stoi, estoi = None, None, None, None
        # result handling
        result = {
            "file": line.strip(),
            "metrics": {
                "Mcd": mcd if mcd else None,
                "Pesq": pesq if pesq else None,
                "Stoi": stoi if stoi else None,
                "Estoi": estoi if estoi else None,
                "Mos": mos
            },
        }
        return result

    except Exception as e:
        # In case of an error
        raise e
    
def eval_dataset(meta: str, dataset_path: str = None, web_mode: bool=False, intrusive: bool=False, file_name: str=None):
    """
        Main function responsible for evaluation
        goes through every line in meta file and gets audio names
        and evalutes them

        Params:
            meta:           meta file path, containing meta data
            dataset_path:   dataset path containing audios
            web_mode:       flag, responsible for logging into CLI console or to the web application
    """
    log_event("Evaluation started.", web_mode)
    if not file_name:
        file_name = os.path.join(UPLOAD_PATH, RESULTS_FILE)
    else:
        file_name = os.path.join(UPLOAD_PATH, file_name)
    # Get all lines in meta file
    with open(meta, "r") as f:
        lines = f.readlines()

    # json output result
    results_data = {
        "status": "running",
        "path": dataset_path,
        "intrusive": intrusive,
        "results": []
    }
    save_results(results_data, file_name)

    max_workers = max(1, os.cpu_count() // 2)
    #Max workers is set to half of cpu count, can be upped

    # Parallelisation of evaluation
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_line, line, dataset_path, web_mode, intrusive) for line in lines]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results_data["results"].append(result)
                save_results(results_data, file_name)
                log_event(result, web_mode=web_mode)
            except Exception as e:
                log_event(e, web_mode=web_mode)
                log_event("Please check your meta file, audio files or selected mode of evaluation.", web_mode=web_mode)
                continue

    #End of an evaluation
    results_data["status"] = "completed"
    #Flag for completed evaluation
    save_results(results_data, file_name)

    log_event("Evaluation completed.", web_mode)
    log_event(load_audios(UPLOAD_PATH, SAMPLES_PATH))
    delete_temp_files()
