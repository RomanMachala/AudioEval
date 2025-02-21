from fastapi import FastAPI, BackgroundTasks, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import pandas as pd
from plots.analysis import analysis
from eval_dataset import get_audios, eval_audio

class EvaluationRequest(BaseModel):
    meta_file: str
    dataset_path: str

app = FastAPI()
RESULTS_FILE    = "results.json"
GRAPHS_PATH     = 'static/graphs'
UPLOAD_PATH     = 'uploads'

def save_results(data):
    with open(RESULTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return {"status": "idle", "progress": 0, "results": []}

@app.post("/start-evaluation/")
def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    # Extracting values from the body
    meta_file = request.meta_file
    dataset_path = request.dataset_path

    #Checks whether input values are valid
    if not os.path.exists(meta_file):
        return {"message": "Selected meta file doesn't exist"}
    if not os.path.exists(dataset_path):
        return {"message": "Selected dataset path doesn't exist"}


    # Adding the background task if values are valid
    background_tasks.add_task(eval_dataset, meta_file, dataset_path)

    return {"message": "Evaluation started"} # Info about starting the eval


@app.get("/results/")
def get_results():
    return load_results()

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
        "pesq": [],
        "stoi": [],
        "estoi": [],
        "mcd": [],
        "mos": []
    }
    metrics = ['pesq', 'stoi', 'estoi', 'mcd', 'mos']

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
                    analysis(data, metric, plot_path)
                    web_path = plot_path.replace("static" + os.sep, "/static/")
                    web_path = web_path.replace("\\", "/")  # Převod na webový formát

                    generated_plots[metric].append(web_path)
        except ValueError:
            continue

    if not generated_plots:
        return JSONResponse(status_code=400, content={"error": "No valid file was processed."})
    return {"generated_plots": generated_plots}


def update_plots():
    
    with open(RESULTS_FILE, "r") as f:
        results = json.load(f)
    
        df = pd.DataFrame(results['results'])
        for metric in ["mcd", "pesq", "stoi", "estoi"]:
            if metric in df.columns:
                analysis(df, metric, GRAPHS_PATH)


app.mount("/static", StaticFiles(directory="static"), name="static")

def eval_dataset(meta: str, dataset_path: str = None):
    """
    Main function used for dataset evaluation

    Params:
        meta            : name of the meta file, please refer to readme
                        for correct meta structure
        dataset_path    : in case meta file contains relative paths 
    """
    results = {"status": "running", "progress": 0, "results": []}
    save_results(results)
    
    with open(meta, "r") as f:
        lines = f.readlines()
    total = len(lines)
    
    for i, line in enumerate(lines):
        try:
            ref_audio, gen_audio = get_audios(line=line, dataset_path=dataset_path)
            mcd, pesq, stoi, estoi = eval_audio(ref_audio=ref_audio, gen_audio=gen_audio)
            result = {"file": line.strip(), "mcd": mcd, "pesq": pesq, "stoi": stoi, "estoi": estoi}
        except Exception as e:
            result = {"file": line.strip(), "error": str(e)}
        
        results["progress"] = float(f"{((i / total) * 100):.2f}")
        results["results"].append(result)
        save_results(results)
        #update_plots()
    
    results["status"] = "completed"
    save_results(results)