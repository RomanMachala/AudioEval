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
import time
import asyncio

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
async def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    meta_file = request.meta_file
    dataset_path = request.dataset_path

    if not os.path.exists(meta_file):
        return JSONResponse(content={"message": "Selected meta file doesn't exist"}, status_code=400)
    if not os.path.exists(dataset_path):
        return JSONResponse(content={"message": "Selected dataset path doesn't exist"}, status_code=400)

    background_tasks.add_task(eval_dataset, meta_file, dataset_path, True)

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
                    web_path = web_path.replace("\\", "/")

                    generated_plots[metric].append(web_path)
        except ValueError:
            continue

    if not generated_plots:
        return JSONResponse(status_code=400, content={"error": "No valid file was processed."})
    return {"generated_plots": generated_plots}

def eval_dataset(meta: str, dataset_path: str = None, web_mode=False):
    """
    """
    log_event("Evaluation started.", web_mode)

    with open(meta, "r") as f:
        lines = f.readlines()
    total = len(lines)

    results_data = {
        "status": "running",
        "progress": 0,
        "results": []
    }
    save_results(results_data)
    for i, line in enumerate(lines):
        try:
            log_event(f"Evaluating file: {line.strip()}", web_mode)
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
            log_event(f"Evaluatin of files: {line.strip()} done", web_mode)
            log_event(f"mcd: {mcd}, Pesq: {pesq}, Stoi: {stoi}, Estoi: {estoi}, MOS: {mos}", web_mode)
            log_event(f"", web_mode)
            results_data["results"].append(result)
            results_data["progress"] = int(((i + 1) / total) * 100)
            save_results(results_data)

        except Exception as e:
            log_event(f"Error evaluating {line.strip()}: {str(e)}", web_mode)
            continue

    results_data["status"] = "completed"
    results_data["progress"] = 100
    save_results(results_data)

    log_event("Evaluation completed.", web_mode)


log_messages = []

def log_event(message, web_mode=False):

    if web_mode:
        global log_messages
        log_messages.append(message)
        if len(log_messages) > 100:
            log_messages.pop(0)
    else:
        print(message)

async def log_generator():
    last_log_index = 0
    while True:
        if last_log_index < len(log_messages):
            for log in log_messages[last_log_index:]:
                yield f"data: {log}\n\n"
            last_log_index = len(log_messages)

        await asyncio.sleep(1)

@app.get("/log-stream/")
async def stream_logs():
    return StreamingResponse(log_generator(), media_type="text/event-stream")

app.mount("/static", StaticFiles(directory="static"), name="static")
