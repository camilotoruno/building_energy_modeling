#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 09:58:26 2024

@author: camilotoruno
"""


import xml.etree.ElementTree as ET
import os 
import subprocess
import json
import shutil
from tqdm import tqdm
       
def find_file_w_name_fragment(name_fragment, path):
    # return the first file with a given name_fragment in its file name
    for root, dirs, files in os.walk(path):
        for file in files:
            if name_fragment in file:
                return os.path.join(root, file)


def modify_and_run(buildings, **kwargs):
    
    """
    Iterates through filenames, modifies a JSON entry, and executes OpenStudio workflow.
    
    Args:
      filenames: A list of filenames.
      osw_path: The path to the JSON file to modify.
      cli_command: The OpenStudio CLI command string.
    
    Raises:
      ValueError: If the JSON file cannot be loaded or modified.
      subprocess.CalledProcessError: If the OpenStudio CLI command fails.
    """
    
    # load arguments 
    openstudio_workflow_folder = kwargs.get('openstudio_workflow_folder')
    openstudio_working_dir = kwargs.get("openstudio_working_dir")
    osw_path = kwargs.get("osw_path")
    verbose= kwargs.get('verbose')

    if not os.path.exists(osw_path):
        msg = f'Openstudio workflow {osw_path} not found'
        raise FileNotFoundError(msg) 
    if not os.path.exists(openstudio_working_dir):
        raise FileNotFoundError(f'Openstudio directory {openstudio_working_dir} not found')
    
    # construct the command line call to openstudio
    openstudio_workflow = kwargs.get('openstudio_workflow')
    openstudio_path = kwargs.get('openstudio_path')
    cli_command = f"{openstudio_path} run --workflow workflow/{openstudio_workflow} --measures_only"

    
    ET.register_namespace("", "http://hpxmlonline.com/2019/10")
    ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
    ET.register_namespace("", 'http://hpxmlonline.com/2019/10')
    
    # get each folder (one per bldg), and the schedules and xml file in the foler    
    # Use tqdm to iterate with a progress bar
    for bldg in tqdm(buildings, desc="Generating EnergyPlus files", smoothing=0.01): # smoothing near avg time est

        try:
            # Load the JSON file
            with open(osw_path , 'r') as f:
                openstudio_workflow_file = json.load(f)
        
            openstudio_workflow_file['steps'][0]['arguments']['hpxml_path'] = bldg.modified_xml  
            openstudio_workflow_file['steps'][0]['arguments']['output_dir'] = os.path.join('..', 'workflow', 'run')
            # output_dir": "../workflow/run" 

            # Write the modified JSON back
            with open(osw_path, 'w') as f:
                json.dump(openstudio_workflow_file, f, indent=4)
        
            # call the openstudio command line interface
            result = subprocess.run(
                cli_command,
                shell=True,  # Set to False if not using shell features
                cwd=openstudio_working_dir,
                capture_output=True,
                text=True
                )
            
            # Check for errors and process the output
            if result.returncode != 0:
                print("Error running OpenStudio:", result.stderr)
            if verbose:
                print("OpenStudio output:", result.stdout)


            bldg.filebasename = "bldg" + bldg.id + "_" + bldg.weather_scenario
            
            # copy the generated .idf file to the correct output folder
            generated_idf = os.path.join(openstudio_workflow_folder, 'run', 'in.idf')
            output_idf = os.path.join(bldg.folder, bldg.filebasename + ".idf")
            shutil.copy(generated_idf, output_idf)
            
            # copy the generated schedules file to the correct output folder and save name to bldg object
            search_path = os.path.join(openstudio_workflow_folder, "generated_files")
            generated_schedule = find_file_w_name_fragment('schedule', search_path)  # find schedules file in openstudio output folder
            shutil.copy(generated_schedule, bldg.folder)
            bldg.schedules_new = os.path.basename(generated_schedule)

            # copy the run log
            shutil.copy(os.path.join(openstudio_workflow_folder, 'run', 'run.log'), os.path.join(bldg.folder, bldg.filebasename + "_osw.log"))
            # buildings[i].schedules_new = os.path.join(bldg.folder, os.path.split(generated_schedule)[1])
        
        # raise errors if they occured while reading openstudio json file
        except (ValueError, json.JSONDecodeError) as e:
            raise Exception(f"Error modifying JSON for file {bldg.xml}: {e}")
    
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error running OpenStudio CLI for file {bldg.xml}: {e}")
                
        
    return buildings
    
    
    
    
    
    
    
    
    
