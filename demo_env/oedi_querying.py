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
        
        
def download_files(s3, bldg_obj_lst, **kwargs):
    fails = 0
    failed = []

    # Use tqdm to iterate with a progress bar
    for bldg in tqdm(bldg_obj_lst, desc="Downloading files", smoothing=0.01): # near average smoothing of est time
        # Increment counter after each successful download        
        try:             
            s3.download_file(Bucket="oedi-data-lake", 
                                Key= bldg.oedi_zip_fldr,
                                Filename = bldg.zip
                                )
        except: 
            raise FileNotFoundError('Building', bldg.id, 'failed to download. File likely not on OEDI\n\n')
            # break
            fails += 1
            failed.append(bldg.oedi_zip_fldr)
        
    if fails !=0: print(fails, 'files failed to download')

        
def download_unzip(building_objects_list, **kwargs):    
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
    
    download_files(s3, building_objects_list, **kwargs)
    if unzip: 
        unzip_files(building_objects_list)

        # update the bldg objects with new files 
        for i in range(len(building_objects_list)):
            building_objects_list[i].assign_folders_contents()
        
    return building_objects_list
