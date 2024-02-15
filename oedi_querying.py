#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 16:45:12 2024

@author: camilotoruno
"""

import boto3
import pandas as pd
from botocore import UNSIGNED
from botocore.client import Config
import zipfile
import os
import shutil
import time
import numpy as np

def create_folder_with_prompt(folder_path):
    skip = False
    """Creates a folder with user confirmation for overwrite."""
    print("\n\n")
    if os.path.exists(folder_path):
        overwrite = input(f"Folder '{folder_path}' already exists. Overwrite? (y/n): \n")
        if overwrite.lower() == 'y':
            shutil.rmtree(folder_path)  # Remove existing folder
            os.mkdir(folder_path)  # Create a new one
            print(f"Folder '{folder_path}' overwritten successfully.")
        else:
            print(f"Folder '{folder_path}' was not overwritten.")
            skip = True
    else:
        os.mkdir(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
        
    return skip

def generate_bldg_foldernames():
    # bldg zip folder names generated to match the naming scheme on OEDI
    bldg_zip_files = []
    for i, bldg_id in enumerate(buildstock.bldg_id.values):
        bldg_id = str(bldg_id)
        bldg_id = bldg_id.zfill(7) # padd the building number with zeros
        bldg_zip = "bldg" + bldg_id + "-up00.zip"  # add the prefix and suffix to filename
        bldg_zip_files.append(bldg_zip)  
        
    return bldg_zip_files


def unzip_files(bldg_zip_files):
    startTime = time.time()   
    for i, bldg_zip in enumerate(bldg_zip_files): 
        zip_path = os.path.join(download_folder, zip_folder, bldg_zip)
        unzip_path = os.path.join(download_folder, unzip_folder, bldg_zip.split('.')[0])
        try: 
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(unzip_path)
            
        except: 
            print('\nWarning:', zip_path, 'failed to unzip')
            print(unzip_path)
            break
        
        duration = (time.time() - startTime)/60
        rate = (i+1)/duration 
        est_time_min = (len(buildstock)+1)/rate
        print('\r', str(i+1), '/', len(buildstock), 'unzipped.', 
              "Estimated time remaining", round(est_time_min - duration, 1), 
              'minutes.',  end='', flush=True)
        
        
def download_files(bldg_zip_files):
    startTime = time.time()   
    fails = 0
    failed = []
    for i, bldg_zip in enumerate(bldg_zip_files): 
    
        try: 
            s3.download_file(Bucket="oedi-data-lake", 
                                Key= oedi_filepath + bldg_zip,
                                Filename = download_folder + zip_folder + bldg_zip )
        except: 
            print('\nError:', bldg_zip, 'failed to download. File likely not on OEDI\n\n')
            # break
            fails += 1
            failed.append(bldg_zip)
         
        duration = (time.time() - startTime)/60
        rate = (i+1)/duration 
        est_time_min = (len(buildstock)+1)/rate
        print('\r', str(i+1), '/', len(buildstock), 'downloaded.', 
              "Estimated time remaining", round(est_time_min - duration, 1), 
              'minutes.',  end='', flush=True)
    
    if fails !=0: print(fails, 'files failed to download')


def download_unzip_files(unzip=True):         
        
    print('Downloading', len(buildstock), 'files from OEDI', end="")
    if unzip: print(' and unzipping files')
    else: print()
    
    bldg_zip_files = generate_bldg_foldernames()
    download_files(bldg_zip_files)
    if unzip: unzip_files(bldg_zip_files)
    
            
buildstock = pd.read_csv("/Users/camilotoruno/anaconda3/envs/research/research_data/filtered_24.02.11baseline_metadata_only.csv")
oedi_filepath = "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/building_energy_models/upgrade=0/"
download_folder = "/Users/camilotoruno/anaconda3/envs/research/research_data/"
zip_folder = "zipped_building_energy_models/"
unzip_folder = "building_energy_models/"
s3 = boto3.client('s3', config = Config(signature_version = UNSIGNED))

# Check for existing output folders
skip1 = create_folder_with_prompt(download_folder + zip_folder)
skip2 = create_folder_with_prompt(download_folder + unzip_folder)

# downlod / unzip files
if not (skip1 or skip2): download_unzip_files(unzip=False)



