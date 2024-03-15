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
import math 
import multiprocessing
import threading 
import queue
import time 
from tqdm import tqdm 

from botocore import UNSIGNED
from botocore.client import Config

def create_bldg_folder(folder_path, verbose):
    """Creates a folder with user confirmation for overwrite."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Remove existing folder
        os.mkdir(folder_path)  # Create a new one
        if verbose: print(f"Folder '{folder_path}' overwritten successfully.")
    else:
        os.makedirs(folder_path)
        

def generate_bldg_foldernames(building_objects_list, bldg_download_folder_basename, **kwargs):
    # bldg zip folder names generated to match the naming scheme on OEDI
    
    for i, bldg in enumerate(building_objects_list):
        # construct the zip folder name from the id and scenario (-up-00 means upgrade 0)
        
        building_objects_list[i].id = str(bldg.id).zfill(7) # padd the building number with zeros
        
        # generate the oedi folder name and the download folder name
        bldg_zip = "bldg" + building_objects_list[i].id + "-up00.zip"  # add the prefix and suffix to filename
        building_objects_list[i].oedi_zip_fldr = os.path.join(kwargs.get('oedi_filepath'), bldg_zip)
        building_objects_list[i].zip = os.path.join(kwargs.get('oedi_download_folder'), bldg_download_folder_basename, bldg.city, bldg_zip)
        building_objects_list[i].folder = building_objects_list[i].zip.split('.zip')[0]
        
    return building_objects_list


def unzip_files(building_objects_list):    
    for bldg in building_objects_list:
        try: 
            with zipfile.ZipFile(bldg.zip, 'r') as zip_ref:
                zip_ref.extractall(bldg.folder)
            
        except: 
            raise Exception('\nError:', bldg.zip, 'failed to unzip')
            break              
        
        
def download_worker(q, s3):
    while True:
        bldg = q.get()
        if bldg is None:
            break  # Sentinel value to signal thread termination
        try:
            s3.download_file(
                Bucket="oedi-data-lake",
                Key=bldg.oedi_zip_fldr,
                Filename=bldg.zip
            )
        except Exception as e:
            raise FileNotFoundError(f"Building {bldg.id} failed to download. Error: {e}")
        q.task_done()  # Signal task completion for queue management


        
def download_unzip(building_objects_list, **kwargs): 
    startTime = time.time()

    # laod arguments 
    unzip = kwargs.get('unzip') 
    verbose = kwargs.get('verbose')   
        
    # oedi has a standard form for how a bldg id maps to a folder name, generate it
    building_objects_list = generate_bldg_foldernames(building_objects_list, **kwargs)
    
    # overwrite download folder 
    download_folder = os.path.join(kwargs.get('oedi_download_folder'), kwargs.get('bldg_download_folder_basename'))
    if os.path.exists(download_folder):
        shutil.rmtree( download_folder )  # Remove existing folder
        os.mkdir( download_folder )  # Create a new one
    
    s3 = boto3.client('s3', config = Config(signature_version = UNSIGNED))
    
    # Create / check for building folders
    for bldg in building_objects_list:
        create_bldg_folder(os.path.split(bldg.folder)[0], verbose)

    print(f'Downloading {len(building_objects_list)} building files from OEDI...')
    print(f"Rough download time estimate: {round(0.1375*len(building_objects_list)/60, 2)} min")

    # Create a progress bar with total number of buildings
    # pbar = tqdm(total=len(building_objects_list), desc="Downloading OEDI files", smoothing=0.01)
    # num_threads = math.floor(multiprocessing.cpu_count() * (3/4)) * 40
    num_threads = 400
    download_queue = queue.Queue()

    # Create worker threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=download_worker, args=(download_queue, s3))
        thread.start()
        threads.append(thread)

    # Add download tasks to the queue and update progress bar
    for bldg in building_objects_list:
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
    print(f"{len(building_objects_list)} files downloaded in: {hours:02d}hr:{minutes:02d}min:{seconds:02d}sec \n")

    if unzip: 
        unzip_files(building_objects_list)

        # update the bldg objects with new files 
        for i in range(len(building_objects_list)):
            building_objects_list[i].assign_folders_contents()
        
    return building_objects_list
