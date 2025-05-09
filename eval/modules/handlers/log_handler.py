"""
    This file contains logging logic for displaying progress of evaluation.
"""
import asyncio
import sys
import json
import numpy as np

log_messages = list()
last_log_index = 0

async def log_generator():
    """
        Returns logs to be displayed. Checks every 5 sec.
    """
    global last_log_index
    while True:
        current_length = len(log_messages)
        if last_log_index > current_length:
            last_log_index = 0
        if last_log_index < current_length:
            for log in log_messages[last_log_index:]:
                yield f"data: {convert(log)}\n\n"
            last_log_index = len(log_messages)

        await asyncio.sleep(2)

def log_event(message:str, web_mode: bool=False):
    """
        Simple fucntion for logging logic

        Params:
            message:        message to be logged
            web_mode:       flag whether to log into CLI or send to client
    """
    if web_mode:
        global log_messages
        if len(log_messages) > 100:
            log_messages = list()
        log_messages.append(message)

    else:
        print(message)
        sys.stdout.flush()

def save_results(data, file_name:str):
    """
        Simple function that saves current data to the output json file

        Params:
            data:       data to be saved
            file_name:  name of the file
    """
    with open(file_name, "w") as f:
        # opens file and dumps content
        json.dump(data, f, indent=4, default=convert)

def convert(obj):
    """
        Help function to convert np.float values to json friendly values

        Params:
            obj:        object to be converted
        
        Returns:
            converted object
    """
    if isinstance(obj, dict):
        return {k: convert(v) for k, v in obj.items()}
    elif isinstance(obj, np.generic):
        return obj.item()
    else:
        return obj