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
import argparse

def create_folder_with_prompt(folder_path, overwrite):
    skip = False
    """Creates a folder with user confirmation for overwrite."""
    print("\n\n")
    if os.path.exists(folder_path):
        if overwrite:
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

def generate_bldg_foldernames(buildstock):
    # bldg zip folder names generated to match the naming scheme on OEDI
    bldg_zip_files = []
    for i, bldg_id in enumerate(buildstock.bldg_id.values):
        bldg_id = str(bldg_id)
        bldg_id = bldg_id.zfill(7) # padd the building number with zeros
        bldg_zip = "bldg" + bldg_id + "-up00.zip"  # add the prefix and suffix to filename
        bldg_zip_files.append(bldg_zip)  
        
    return bldg_zip_files


def unzip_files(buildstock, bldg_zip_files, **kwargs):
    download_folder = kwargs.get("download_folder")
    zip_folder = kwargs.get("zip_folder")
    unzip_folder = kwargs.get("unzip_folder")
    
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
        
        
def download_files(buildstock, s3, bldg_zip_files, **kwargs):
    
    
    
    startTime = time.time()   
    fails = 0
    failed = []
    
    for i, bldg_zip in enumerate(bldg_zip_files): 
    
        try: 
            s3.download_file(Bucket="oedi-data-lake", 
                                Key= kwargs.get("oedi_filepath") + bldg_zip,
                                Filename = kwargs.get("download_folder") + kwargs.get("zip_folder") + bldg_zip )
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

        
def download_unzip(**kwargs):
    
    buildstock_file = kwargs.get('buildstock_file') 
    download_folder = kwargs.get('download_folder') 
    zip_folder = kwargs.get('zip_folder') 
    unzip_folder = kwargs.get('unzip_folder') 
    unzip = kwargs.get('unzip') 
    overwrite = kwargs.get('overwrite')
    
    # Access parsed arguments
    buildstock = pd.read_csv(buildstock_file)

    # Rest of your script's logic using these values
    s3 = boto3.client('s3', config = Config(signature_version = UNSIGNED))
    
    # Check for existing output folders
    skip1 = create_folder_with_prompt(download_folder + zip_folder, overwrite)
    skip2 = create_folder_with_prompt(download_folder + unzip_folder, overwrite)
    
    # downlod / unzip files
    if not (skip1 or skip2):
            
        print('Downloading', len(buildstock), 'files from OEDI', end="")
        if unzip: print(' and unzipping files')
        else: print()
        
        bldg_zip_files = generate_bldg_foldernames(buildstock)
        download_files(buildstock, s3, bldg_zip_files, **kwargs)
        if unzip: unzip_files(buildstock, bldg_zip_files, **kwargs)
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process building energy model files")

    # Add arguments with appropriate types and help messages
    parser.add_argument("buildstock_file", type=str, help="Absolute Path to the buildstock CSV file")
    parser.add_argument("oedi_filepath", type=str, help="Absolute Path to the OEDI files within the downloaded folder")
    parser.add_argument("download_folder", type=str, help="Absolute Path to the folder containing downloaded files")
    parser.add_argument("zip_folder", type=str, help="Output building zip folder")
    parser.add_argument("unzip_folder", type=str, help="Output folder for unzipped buildings")
    parser.add_argument("--unzip", action="store_true", help="Unzip downloaded files")

    args = parser.parse_args()

    download_unzip(**vars(args))    

