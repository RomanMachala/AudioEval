"""
    Simple script for temp files deletion
"""
import shutil
import os
from modules.constants import UPLOAD_DIR, UPLOAD_PATH, SAMPLES_PATH, GRAPHS_PATH

def delete_temp_files():
    """
        Deletes uploaded audio samples after evalaution.
    """
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)

def clear_cache():
    """
        Clears application cache-deletes all analysis files (graphs, ...)
    """
    if os.path.exists(UPLOAD_PATH):
        shutil.rmtree(UPLOAD_PATH)

    if os.path.exists(SAMPLES_PATH):
        shutil.rmtree(SAMPLES_PATH)

    if os.path.exists(GRAPHS_PATH):
        shutil.rmtree(GRAPHS_PATH)