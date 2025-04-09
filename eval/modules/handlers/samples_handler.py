import os
import json
import shutil
import pandas as pd
from modules.constants import NUM_OF_SAMPLES


def handle_filename(filename: str, datasetpath: str) -> str:
    """
        Function to handle filenames for sample loading

        Params:
            filename:       line in metafile
            datasetpath:    specified datasetpath, if set

        returns:
            path to the sample or None if not exists
    """
    try:
        if " " in filename:
            ref, gen = filename.split(" ")
        else:
            gen = filename
        
        if datasetpath:
            file_path = os.path.join(datasetpath, gen)
        else:
            file_path = gen
        if os.path.exists(file_path):
            return file_path
        else:
            return None
    except Exception:
        return None
    
def move_audios(audio_name: str, audio_path: str, sample_path: str, file_name: str) -> str:
    """
        Function to create a copy of audio samples

        Params:
            audio_name:         name of the sample file
            audio_path:         path to the sample file
            sample_path:        path to the copies of samples
            file_name:          name of the evalaution file result

        Returns:
            path to the sample
    """
    dst_path = os.path.join(sample_path, file_name) # Creates new folder for each result file (better structure)
    dst_path = dst_path.replace('\\', '/') # For web paths
    os.makedirs(exist_ok=True, name=dst_path) #Make sure the folder exists
    dst = os.path.join(dst_path, audio_name) # dst path for sample
    dst = dst.replace('\\', '/')
    if not os.path.exists(dst): # if audio is not copied, make a copy
        shutil.copy(audio_path, dst)

    return dst

def load_audios(upload_path: str, sample_path:str):
    """
        Function to load audios from evaluation files, creates copies in web environment
        and returns paths to those copies for listening tests in web

        Params:
            upload_path:        folder containing uploaded files
            sample_path:        dst path containing copies of samples
    """
    samples = {

    }
    # for each uplaoded file
    for file in os.listdir(upload_path):
        file_path = os.path.join(upload_path, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            datatset_path = data['path']
        raw_data = pd.DataFrame(data['results'])
        audios = raw_data['file'].tolist()
        audios_sorted = sorted(audios)
        for i in range(NUM_OF_SAMPLES): # Get x samples
            if len(audios) <= i:
                break
            filename = audios_sorted[i]
            audio_path = handle_filename(filename, datatset_path)
            if not audio_path:  # if file doesnt exist
                web_path = None
            else: # else create a copy
                audio_name = os.path.basename(audio_path)
                file_name = file.split('.')[0]
                temp = move_audios(audio_name, audio_path, sample_path, file_name)
                web_path = temp.replace('\\', '/')
            if i == 0:
                samples[f"{file.split('.')[0]}"] = list()
            if web_path:
                samples[f"{file.split('.')[0]}"].append(web_path)

    return samples