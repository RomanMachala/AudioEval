"""
    This file contains main logic and endpoints definiton for
    audio evaluation tool. This project is major part of Bachelor's Thesis at BUT Faculty
    of information technology - Comparison and analysis of speech synthesizers.
"""
__author__      = "Roman Machala"
__date__        = "31.03.2025"
__version__     = "0.1"         #stable version
from fastapi import FastAPI, BackgroundTasks, File, UploadFile, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import pandas as pd
from modules.plots.analysis import analysis, table, is_valid
from modules.eval_dataset import eval_dataset
from modules.handlers.log_handler import log_messages, log_generator
from modules.handlers.samples_handler import load_audios
from modules.handlers.file_handler import clear_cache
from modules.constants import UPLOAD_PATH, GRAPHS_PATH, PLOTS_RESULT, SAMPLES_PATH, UPLOAD_DIR
import sys
import copy

class EvaluationRequest(BaseModel):
    """
        Evaluation request model, contains meta_file 
        and dataset_path
    """
    meta_file: str
    root_folder: str
    intrusive: bool
    save_name: str

#Global variables
app = FastAPI()
log_messages = log_messages

@app.get("/")
async def read_index():
    """
        Simple nedpoint for HTML doc return
    """
    return FileResponse("index.html")

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
    dataset_path = os.path.join(UPLOAD_DIR, request.root_folder)
    meta_file = os.path.join(dataset_path, request.meta_file)

    intrusive = request.intrusive
    filename = None if len(request.save_name) < 1 else request.save_name + '.json'
    #TODO handle filename to actually save as desired name

    # Checks for existence of parameters
    if not os.path.exists(meta_file):
        return JSONResponse(content={"message": f"Meta file doesn't exists - {request.meta_file}"}, status_code=400)
    if not os.path.exists(dataset_path):
        return JSONResponse(content={"message": "Files were not uploaded correctly."}, status_code=400)
    # Start evaluation as background task
    os.makedirs(UPLOAD_PATH, exist_ok=True)
    background_tasks.add_task(eval_dataset, meta_file, dataset_path, True, intrusive, file_name=filename)
    # Return response
    return JSONResponse(content={"message": "Evaluation started"}, status_code=200)

@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    """
        Endpoint logic for uploading analysis configuration files

        Params:
            files:      contains uploaded files
    """
    os.makedirs(exist_ok=True, name=UPLOAD_PATH)
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
    os.makedirs(exist_ok=True, name=UPLOAD_PATH)
    os.makedirs(exist_ok=True, name=GRAPHS_PATH)
    # dict for graphs paths
    generated_plots = copy.deepcopy(PLOTS_RESULT)

        # Goes through all files in upload path folder
    for filename in os.listdir(UPLOAD_PATH):
        file_path = os.path.join(UPLOAD_PATH, filename)
        print(filename)
        try:
            with open(file_path, 'r') as f:
                # Gets file content
                raw_data = json.load(f)
            # Creates dataframe
            rows = []
            for file, metrics in [(i['file'], i['metrics']) for i in raw_data['results']]:
                metrics['file'] = file
                rows.append(metrics)

            data = pd.DataFrame(rows)
            file_name = os.path.splitext(filename)[0]
            # For each metric that is in column of said dataframe
            # creates a graph and adds it into the dict
            for metric in data.columns:
                if metric != 'file':
                    if file_name not in generated_plots['tables']['Files']:
                        generated_plots['tables']['Files'].append(file_name)
                    plot_path = os.path.join(GRAPHS_PATH, f'{file_name}_{metric}.png')
                    if is_valid(data, metric):
                        web_path = plot_path.replace("static" + os.sep, "/static/")
                        web_path = web_path.replace("\\", "/")
                        if not os.path.exists(web_path):
                            analysis(data, metric, plot_path, file_name)
                        values = table(data, metric)
                        if metric != 'Mos':
                            if metric not in generated_plots['tables']['Values']:
                                generated_plots['tables']['Values'][metric] = list()
                            generated_plots['tables']['Values'][metric].append(values)
                        else:
                            generated_plots['tables']['Values']['ovrl_mos'].append(values[0])
                            generated_plots['tables']['Values']['sig_mos'].append(values[1])
                            generated_plots['tables']['Values']['bak_mos'].append(values[2])
                            generated_plots['tables']['Values']['p808_mos'].append(values[3])
                    else:
                        web_path = None
                        if metric not in generated_plots['tables']['Values']:
                            generated_plots['tables']['Values'][metric] = list()
                        generated_plots['tables']['Values'][metric].append([None, None, None, None])
                    # adds generated graph path to corresponding metric in dict
                    if metric not in generated_plots['plots']:
                        generated_plots['plots'][metric] = list()
                    generated_plots['plots'][metric].append(web_path)
        except ValueError:
            #TODO better handling, if and exception occurs skips it
            continue
    # If there are no generated plots just return error
    if not generated_plots:
        return JSONResponse(status_code=400, content={"error": "No valid file was processed."})
    # Else returns dictionary containing generated graphs paths
    return {"generated_plots": generated_plots}

@app.post("/upload-files")
async def upload_files(request: Request):
    """
        Endpoint for uplaoding files, saves files on server side as temporal files
    """
    form = await request.form()

    for key in form:
        file = form[key]
        rel_path = key.replace("\\", "/")
        save_path = os.path.join(UPLOAD_DIR, rel_path)
        #creates temp files
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as buffer:
            buffer.write(await file.read())

    return JSONResponse(content={"status": "success"})

@app.post('/audios/')
async def get_audios():
    """
        Endpoint for audio sample loading.
    """
    samples = load_audios(UPLOAD_PATH, SAMPLES_PATH)

    return {"samples": samples}

@app.get("/log-stream/")
async def stream_logs():
    """
        endpoint for log streaming evaluation progress to frontend
    """
    return StreamingResponse(log_generator(), media_type="text/event-stream")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/clear_cache/")
async def empty_cache():
    """
        Endpoint for cache clearing - removes all previous analysis'
    """
    try:
        clear_cache()
        return JSONResponse(content={"status": "Success"}, status_code=200)
    except:
        return JSONResponse(content={"status": "Error"}, status_code=400)

if __name__ == "__main__":
    #TODO CLI WAY
    from modules.handlers.arg_handler import handle_arguments
    #FOR CLI EVALUATION ONLY 
    meta, dataset, save, intrusive = handle_arguments(sys.argv)
    eval_dataset(meta=meta, dataset_path=dataset, web_mode=False, intrusive=True if intrusive == 'true' else False, file_name=save)
