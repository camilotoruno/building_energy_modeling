#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 16:45:12 2024

@author: camilotoruno
"""

import boto3
import zipfile
import os
import shutil
import threading 
import queue
import time 
import warnings 
import tqdm 
from pathlib import Path
from datetime import datetime

from botocore import UNSIGNED
from botocore.client import Config

def unzip_files(building_objects_list):    
    for bldg in tqdm.tqdm(building_objects_list, total=len(building_objects_list), desc='Unzipping OEDI folders', smoothing=0.01):
        try: 
            with zipfile.ZipFile(bldg.zip, 'r') as zip_ref:
                zip_ref.extractall(bldg.folder)

            if not Path(Path(bldg.folder).parents[0], "schedules.csv").exists():   # if we've not yet copied the schedules to the parent folder 
                shutil.copy(Path(bldg.folder, "schedules.csv"),  Path(Path(bldg.folder).parents[0], "schedules.csv"))  # copy the schedules file to the building-weather year folder to the building parent directory 

            if Path(bldg.folder, "schedules.csv").exists(): os.remove(Path(bldg.folder, "schedules.csv"))   # delete the building-weather year's local copy of the schedules to reduce data storage requriement 

        except: 
            raise RuntimeError('\nError:', bldg.zip, 'failed to unzip')
        
        
def download_worker(q, s3):
    while True:
        bldg = q.get()
        if bldg is None:
            break  # Sentinel value to signal thread termination
        try:
            s3.download_file(
                Bucket="oedi-data-lake",
                Key=bldg.oedi_zip_fldr,
                Filename=bldg.zip)
        except Exception as e:
            raise RuntimeError(f"Building {bldg.id} failed to download. Error: {e}")
        q.task_done()  # Signal task completion for queue management


def file_check(**kwargs): 
    download_folder = Path(kwargs.get('oedi_download_folder'), kwargs.get('bldg_download_folder_basename'))
    
    if not os.path.exists(download_folder):
        print(f'Making output folder {download_folder}')
        os.makedirs( download_folder )  # Create a new one

    elif kwargs.get('overwrite_output'):
        print(f'Warning: Overwriting output folder {download_folder}. Cancel job if overwrite chosen in error.')
        time.sleep(5)
        shutil.rmtree( download_folder )  # Remove existing folder
        os.makedirs( download_folder )  # Create a new one

    else: print(f"Download folder exists and overwrite not enabled. Existing files will be skipped during processing.")


def generate_job_list(building_objects_list, **kwargs):
    jobs = []

    if building_objects_list:    # If a bldg objects list is passed check for folders. 
        for bldg in building_objects_list:          # check for building folders to determine whether to download 
            if not Path(bldg.folder).exists():
                os.makedirs(bldg.folder)  # Create a new one
                jobs.append(bldg)
            
            elif kwargs.get('overwrite_output'):
                if kwargs.get('verbose'): warnings.warn(f"Output building folder '{bldg.folder}' overwritten.")
                shutil.rmtree(bldg.folder)  # Remove existing folder
                os.makedirs(bldg.folder)  # Create a new one                
                jobs.append(bldg)

            elif kwargs.get('verbose'): print(f'\tOutput building folder already exists. Not overwritten: {bldg.folder}')

    return jobs

def download_unzip(building_objects_list, **kwargs): 
    num_threads = 20

    startTime = time.time()

    # laod arguments 
    unzip = kwargs.get('unzip') 
        
    # oedi has a standard form for how a bldg id maps to a folder name, generate it
    jobs = generate_job_list(building_objects_list, **kwargs)

    s3 = boto3.client('s3', config = Config(signature_version = UNSIGNED))   # connect to Amazon S3 API client 

    print(f'Downloading {len(jobs)} building files from OEDI...')
    print(f'Rough download time estimate: {round(0.2865*len(jobs)/60/num_threads, 2)} min. Start time: {datetime.now().strftime("%H:%M:%S")}')

    # Create a progress bar with total number of buildings
    # pbar = tqdm(total=len(building_objects_list), desc="Downloading OEDI files", smoothing=0.01)
    # num_threads = math.floor(multiprocessing.cpu_count() * (3/4)) * 40
    download_queue = queue.Queue()

    # Create worker threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=download_worker, args=(download_queue, s3))
        thread.start()
        threads.append(thread)

    # Add download tasks to the queue and update progress bar
    for bldg in jobs:
        download_queue.put(bldg)
        # pbar.update()  # Update progress bar for each added task

    # Wait for all tasks to finish (using queue.join())
    download_queue.join()

    # Signal termination to worker threads (using sentinel value)
    for _ in range(num_threads):
        download_queue.put(None)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
        
    # Convert elapsed time to hours, minutes, seconds
    elapsed_time = time.time() - startTime
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    print(f"{len(jobs)} files downloaded in: {hours:02d}hr:{minutes:02d}min:{seconds:02d}sec \n")

    if unzip: 
        unzip_files(jobs)

    # update the bldg objects with xml file names
    for i in range(len(building_objects_list)):
        building_objects_list[i].assign_folders_contents()

        if Path(building_objects_list[i].zip).exists():
            os.remove(building_objects_list[i].zip)  # delete the zip file to reduce data storage 
    
    return building_objects_list
