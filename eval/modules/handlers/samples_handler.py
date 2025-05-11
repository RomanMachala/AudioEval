"""
    Script to handle samples loading
"""
import os
import json
import shutil
import pandas as pd
from modules.constants import NUM_OF_SAMPLES


def handle_filename(line: str, datasetpath: str, intrusive: bool) -> tuple[str, str]:
    """
        Function to handle filenames for sample loading

        Params:
            line:       line in metafile

        returns:
            path to the sample or None if not exists
    """
    try:
        if intrusive:
            ref, gen = line.strip().split(" ")
            return os.path.join(datasetpath, ref), os.path.join(datasetpath, gen)
        else:
            ref, gen = None, line.strip().split(" ")[0]
            return None, os.path.join(datasetpath, gen)

    except Exception:
        return None, None
    
def move_audios(ref: str, gen: str, sample_path: str, intrusive: bool, filename: str) -> tuple[str, str, bool]:
    """
        Function to create a copy of audio samples

        Params:
            ref:            reference audio sample path
            gen:            generated audio sample path
            sample_path:    samples dir path


        Returns:
            path to samples
    """
    if intrusive:
        ref_base = os.path.basename(ref)
        gen_base = os.path.basename(gen)
        os.makedirs(os.path.join(sample_path, filename, "ref"), exist_ok=True)
        os.makedirs(os.path.join(sample_path, filename, "gen"), exist_ok=True)
        web_ref = os.path.join(sample_path, filename, "ref", ref_base)
        web_gen = os.path.join(sample_path, filename, "gen", gen_base)
        if not os.path.exists(web_ref):
            if not os.path.exists(ref) or not os.path.exists(gen):
                return None, None, False
            else:
                try:
                    shutil.copy(ref, web_ref)
                except Exception:
                    return None, None, False
        if not os.path.exists(web_gen):
            if not os.path.exists(ref) or not os.path.exists(gen):
                return None, None, False
            else:
                try:
                    shutil.copy(gen, web_gen)
                except Exception:
                    return None, None, False
        return web_ref.replace("\\", "/"), web_gen.replace("\\", "/"), True
    else:
        gen_base = os.path.basename(gen)
        os.makedirs(os.path.join(sample_path, filename, "gen"), exist_ok=True)
        web_gen = os.path.join(sample_path, filename, "gen", gen_base)
        if not os.path.exists(web_gen):
            if not os.path.exists(gen):
                return None, None, False
            else:
                try:
                    shutil.copy(gen, web_gen)
                except Exception:
                    return None, None, False
    
        return None, web_gen.replace("\\", "/"), True
        

def load_audios(upload_path: str, sample_path:str):
    """
        Function to load audios from evaluation files, creates copies in web environment
        and returns paths to those copies for listening tests in web

        Params:
            upload_path:        folder containing uploaded files
            sample_path:        dst path containing copies of samples
            dataset_name:       uploaded folder's name
    """
    samples = {

    }
    # for each uplaoded file
    for file in os.listdir(upload_path):
            file_path = os.path.join(upload_path, file)
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f) 
                    dataset_path = data["path"]
                    intrusive = data["intrusive"]
                    raw_data = pd.DataFrame(data['results']) 
                    audios = raw_data['file'].tolist()
                except Exception as e:
                    print(e)
                    continue    # skip current file with invalid values
            

            i = 0
            for audio in audios:
                if i >= NUM_OF_SAMPLES:
                    break
                ref, gen = handle_filename(audio, dataset_path, intrusive)
                web_ref, web_gen, res = move_audios(ref, gen, sample_path, intrusive, file.split(".")[0])
                if res:
                    if i == 0:
                        samples[f"{file.split('.')[0]}"] = {
                            "ref": list(),
                            "gen": list()
                        }
                    samples[f"{file.split('.')[0]}"]["gen"].append(web_gen)
                    samples[f"{file.split('.')[0]}"]["ref"].append(web_ref)
                    i += 1

    return samples