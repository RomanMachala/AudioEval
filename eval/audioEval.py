from fastapi import FastAPI, BackgroundTasks, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import pandas as pd
from plots.analysis import analysis, table
from eval_dataset import get_audios, eval_audio
import numpy as np
import asyncio
import concurrent.futures

class EvaluationRequest(BaseModel):
    """
        Evaluation request model, contains meta_file 
        and dataset_path
    """
    meta_file: str
    dataset_path: str

"""
    Global variables for evaluation output
    graphs path and upload folder path, log messages
"""
app = FastAPI()
RESULTS_FILE    = "results.json"
GRAPHS_PATH     = 'static/graphs'
UPLOAD_PATH     = 'uploads'
log_messages = []

def save_results(data):
    """
        Simple function that saves current data to the output json file

        Params:
            data:       data to be saved
    """
    with open(RESULTS_FILE, "w") as f:
        # opens file and dumps content
        json.dump(data, f, indent=4, default=convert)

def convert(obj):
    """
        Help function to convert np.float values to json friendly values

        Params:
            obj:        object to be converted
    """
    if isinstance(obj, (np.float32, np.float64, np.int32, np.int64)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


@app.post("/start-evaluation/")
async def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """
        Main function for evaluation starting
        expects json request containing meta_file and dataset_path

        Params:
            request:            dataset_path, meta_file
            background_tasks:   background tasks
    """
    # Extract parameterrs
    meta_file = request.meta_file
    dataset_path = request.dataset_path

    # Checks for existence of parameters
    if not os.path.exists(meta_file):
        return JSONResponse(content={"message": "Selected meta file doesn't exist"}, status_code=400)
    if not os.path.exists(dataset_path):
        return JSONResponse(content={"message": "Selected dataset path doesn't exist"}, status_code=400)
    # Start evaluation as background task
    background_tasks.add_task(eval_dataset, meta_file, dataset_path, True)
    # Return response
    return JSONResponse(content={"message": "Evaluation started"}, status_code=200)


@app.get("/")
async def read_index():
    """
        Simple nedpoint for HTML doc return
    """
    return FileResponse("index.html")

@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    """
        Endpoint logic for uploading analysis configuration files

        Params:
            files:      contains uploaded files
    """
    valid_files = list()
    # list for valid files
    # For each file in uploaded files
    for file in files:
        # Read it' content
        content = await file.read()
        # Get path of uploaded file
        file_path = os.path.join(UPLOAD_PATH, file.filename)

        try:
            # loads it' content, if it fails, excpetion is raised
            data = json.loads(content)
            with open(file_path, 'wb') as f:
                # creates new file in upload path and dumps it' values into it
                f.write(content)
            valid_files.append(file.filename)
        except json.JSONDecodeError:
            continue
    # Returns all valid files 
    return {"message": "Upload complete", "valid_files": valid_files}

@app.post('/process/')
async def process_files():
    """
        Endpoint for uploaded file processing 
        - processes uplaoded files, generates graphs and returns
            graphs paths for vizualization
    """
    # dict for graphs paths
    generated_plots = {
        "Pesq": [],
        "Stoi": [],
        "Estoi": [],
        "Mcd": [],
        "Mos": []
    }
    # All metrics, that are "valid"
    metrics = ['Pesq', 'Stoi', 'Estoi', 'Mcd', 'Mos']

        # Goes through all files in upload path folder
    for filename in os.listdir(UPLOAD_PATH):
        file_path = os.path.join(UPLOAD_PATH, filename)
        try:
            with open(file_path, 'r') as f:
                # Gets file content
                raw_data = json.load(f)
            # Creates dataframe
            data = pd.DataFrame(raw_data['results'])
            file_name = os.path.splitext(filename)[0]
            # For each metric that is in column of said dataframe
            # creates a graph and adds it into the dict
            for metric in metrics:
                if metric in data.columns:
                    plot_path = os.path.join(GRAPHS_PATH, f'{file_name}_{metric}.png')
                    analysis(data, metric, plot_path, file_name)
                    web_path = plot_path.replace("static" + os.sep, "/static/")
                    web_path = web_path.replace("\\", "/")
                    # adds generated graph path to corresponding metric in dict
                    generated_plots[metric].append(web_path)
        except ValueError:
            #TODO better handling, if and exception occurs skips it
            continue
    # If there are no generated plots just return error
    if not generated_plots:
        return JSONResponse(status_code=400, content={"error": "No valid file was processed."})
    # Else returns dictionary containing generated graphs paths
    return {"generated_plots": generated_plots}

@app.post('/get_tables/')
async def get_tables():
    """
        Endpoint for table values calculation.

        Calculated mean, median, min and max values for each file and metric
        and returns these values as json
    """

    # JSON structure
    tables = {
    "Files": [],
    "Values": {
        "Pesq": [],
        "Stoi" : [],
        "Estoi": [],
        "Mcd": [],
        "ovrl_mos": [],
        "sig_mos" : [],
        "bak_mos": [],
        "p808_mos": []
        }
    }
    # Metrics to be calculated
    metrics = ['Pesq', 'Stoi', 'Estoi', 'Mcd', 'Mos']
    # Iterate through uploaded files
    for file in os.listdir(UPLOAD_PATH):
        file_path = os.path.join(UPLOAD_PATH, file)
        file_name = os.path.splitext(file)[0]

        try:
            with open(file_path, 'r') as f:
                # Gets file content
                raw_data = json.load(f)
            # Creates dataframe
            data = pd.DataFrame(raw_data['results'])
            # For each metric that is in column of said dataframe
            # creates a graph and adds it into the dict
            for metric in metrics:
                if metric in data.columns:
                    # Calculate values
                    values = table(data, metric)
                    if metric != 'Mos':
                        tables['Values'][metric].append(values)
                    else:
                        tables['Values']['ovrl_mos'].append(values[0])
                        tables['Values']['sig_mos'].append(values[1])
                        tables['Values']['bak_mos'].append(values[2])
                        tables['Values']['p808_mos'].append(values[3])
            tables['Files'].append(file_name)
        except ValueError:
            #TODO better handling, if and exception occurs skips it
            continue
        if not tables:
            return JSONResponse(status_code=400, content={"error": "No valid file was processed."})
    # Else returns dictionary containing generated graphs paths
    return {"tables": tables}

def process_line(line, dataset_path, web_mode):
    """
        Function to evaluate audios specificated by line in meta file

        Params:
            line:           contains ref and gen audio path
            dataset_path:   path to dataset
            web_mode:       logging mode

        Returns:
            results of evaluation
    """
    try:
        # Gets reference and generated audio
        ref_audio, gen_audio = get_audios(line=line, dataset_path=dataset_path)
        # Gets evaluation
        mcd, pesq, stoi, estoi, mos = eval_audio(ref_audio=ref_audio, gen_audio=gen_audio)
        # result handling
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
        return result

    except Exception as e:
        # In case of an error
        log_event(f"Error evaluating {line.strip()}: {str(e)}", web_mode)
        return None

def eval_dataset(meta: str, dataset_path: str = None, web_mode=False):
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

    # Get all lines in meta file
    with open(meta, "r") as f:
        lines = f.readlines()
    #total = len(lines)

    # json output result
    results_data = {
        "status": "running",
        "results": []
    }
    save_results(results_data)

    max_workers = max(1, os.cpu_count() // 2)
    #Max workers is set to half of cpu count, can be upped

    # Parallelisation of evaluation
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_line, line, dataset_path, web_mode) for line in lines]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results_data["results"].append(result)
                save_results(results_data)


    #End of an evaluation
    results_data["status"] = "completed"
    #Flag for completed evaluation
    save_results(results_data)

    log_event("Evaluation completed.", web_mode)

def log_event(message, web_mode=False):
    """
        Simple fucntion for logging logic

        Params:
            message:        message to be logged
            web_mode:       flag whether to log into CLI or send to client
    """
    if web_mode:
        global log_messages
        log_messages.append(message)
        if len(log_messages) > 100:
            log_messages.pop(0)
    else:
        print(message)

async def log_generator():
    """
        Returns logs to be displayed. Checks every 5 sec.
    """
    last_log_index = 0
    while True:
        if last_log_index < len(log_messages):
            for log in log_messages[last_log_index:]:
                yield f"data: {log}\n\n"
            last_log_index = len(log_messages)

        await asyncio.sleep(5)

@app.get("/log-stream/")
async def stream_logs():
    """
        endpoint for log streaming evaluation progress to frontend
    """
    return StreamingResponse(log_generator(), media_type="text/event-stream")

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    #FOR CLI EVALUATION ONLY 
    #eval_dataset(TODO handle args)
    pass
