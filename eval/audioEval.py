from fastapi import FastAPI, BackgroundTasks, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import pandas as pd
from plots.analysis import analysis
from eval_dataset import get_audios, eval_audio
import numpy as np

class EvaluationRequest(BaseModel):
    meta_file: str
    dataset_path: str

app = FastAPI()
RESULTS_FILE    = "results.json"
GRAPHS_PATH     = 'static/graphs'
UPLOAD_PATH     = 'uploads'

def save_results(data):
    with open(RESULTS_FILE, "w") as f:
        json.dump(data, f, indent=4, default=convert)

def convert(obj):
    if isinstance(obj, (np.float32, np.float64, np.int32, np.int64)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return {"status": "idle", "progress": 0, "results": []}

@app.post("/start-evaluation/")
def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    meta_file = request.meta_file
    dataset_path = request.dataset_path

    if not os.path.exists(meta_file):
        return JSONResponse(content={"message": "Selected meta file doesn't exist"}, status_code=400)
    if not os.path.exists(dataset_path):
        return JSONResponse(content={"message": "Selected dataset path doesn't exist"}, status_code=400)

    background_tasks.add_task(eval_dataset, meta_file, dataset_path)

    return JSONResponse(content={"message": "Evaluation started"}, status_code=200)


@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    valid_files = list()

    for file in files:
        content = await file.read()
        file_path = os.path.join(UPLOAD_PATH, file.filename)

        try:
            data = json.loads(content)
            with open(file_path, 'wb') as f:
                f.write(content)
            valid_files.append(file.filename)
        except json.JSONDecodeError:
            continue

    return {"message": "Upload complete", "valid_files": valid_files}

@app.post('/process/')
async def process_files():
    generated_plots = {
        "Pesq": [],
        "Stoi": [],
        "Estoi": [],
        "Mcd": [],
        "Mos": []
    }
    metrics = ['Pesq', 'Stoi', 'Estoi', 'Mcd', 'Mos']

    for filename in os.listdir(UPLOAD_PATH):
        file_path = os.path.join(UPLOAD_PATH, filename)
        try:
            with open(file_path, 'r') as f:
                raw_data = json.load(f)
            data = pd.DataFrame(raw_data['results'])
            file_name = os.path.splitext(filename)[0]
            for metric in metrics:
                if metric in data.columns:
                    plot_path = os.path.join(GRAPHS_PATH, f'{file_name}_{metric}.png')
                    analysis(data, metric, plot_path, file_name)
                    web_path = plot_path.replace("static" + os.sep, "/static/")
                    web_path = web_path.replace("\\", "/")  # Převod na webový formát

                    generated_plots[metric].append(web_path)
        except ValueError:
            continue

    if not generated_plots:
        return JSONResponse(status_code=400, content={"error": "No valid file was processed."})
    return {"generated_plots": generated_plots}


app.mount("/static", StaticFiles(directory="static"), name="static")

def eval_dataset(meta: str, dataset_path: str = None, log_callback=None):
    """
    Main function used for dataset evaluation

    Params:
        meta            : name of the meta file
        dataset_path    : path to dataset (optional)
        log_callback    : function for logging (optional)
    """
    def log(message):
        if log_callback:
            log_callback(message)  # Pokud existuje callback, voláme ho
        else:
            print(message)  # Jinak tiskneme do konzole

    log("Starting evaluation for files in: " + meta)
    results = {"status": "running", "progress": 0, "results": []}
    save_results(results)

    with open(meta, "r") as f:
        lines = f.readlines()
    total = len(lines)

    for i, line in enumerate(lines):
        try:
            log(f"Processing file {i+1}/{total}: {line.strip()}")
            ref_audio, gen_audio = get_audios(line=line, dataset_path=dataset_path)
            mcd, pesq, stoi, estoi, mos = eval_audio(ref_audio=ref_audio, gen_audio=gen_audio)

            result = {
                "file": line.strip(),
                "Mcd": float(mcd),
                "Pesq": float(pesq),
                "Stoi": float(stoi),
                "Estoi": float(estoi),
                "Mos": convert(mos)
            }

            log(f"Results for {line.strip()} -> PESQ: {pesq}, STOI: {stoi}, ESTOI: {estoi}, MCD: {mcd}, MOS: {mos}")

        except Exception as e:
            log(f"Error processing {line.strip()}: {e}")
            continue

        results["progress"] = float(f"{((i / total) * 100):.2f}")
        results["results"].append(result)
        save_results(results)

    log("Evaluation completed!")

@app.get("/results/")
def get_results():
    if not os.path.exists(RESULTS_FILE):
        return {"status": "not started", "progress": 0, "results": []}

    with open(RESULTS_FILE, "r") as f:
        results = json.load(f)

    return results