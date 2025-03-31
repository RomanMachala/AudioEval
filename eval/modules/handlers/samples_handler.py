import os
import json
import shutil
import pandas as pd

NUM_OF_SAMPLES = 5


def move_audios(audio_name, audio_path, sample_path, file_name) -> str:
    dst_path = os.path.join(sample_path, file_name)
    dst_path = dst_path.replace('\\', '/')
    os.makedirs(exist_ok=True, name=dst_path)
    dst = os.path.join(dst_path, audio_name)
    dst = dst.replace('\\', '/')
    if not os.path.exists(dst):
        shutil.copy(audio_path, dst)

    return dst
def load_audios(upload_path: str, sample_path):
    samples = {

    }

    for file in os.listdir(upload_path):
        file_path = os.path.join(upload_path, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            datatset_path = data['path']
        raw_data = pd.DataFrame(data['results'])
        audios = raw_data['file'].tolist()
        audios_sorted = sorted(audios)
        for i in range(NUM_OF_SAMPLES):
            filename = audios_sorted[i]
            if datatset_path:
                audio_path = os.path.join(datatset_path, filename)
            else:
                audio_path = filename
            audio_name = os.path.basename(audio_path)
            file_name = file.split('.')[0]
            temp = move_audios(audio_name, audio_path, sample_path, file_name)
            web_path = temp.replace('\\', '/')
            if i == 0:
                samples[f'{file.split('.')[0]}'] = list()
            samples[f'{file.split('.')[0]}'].append(web_path)

    return samples
