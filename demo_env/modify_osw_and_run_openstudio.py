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
import xml_modifier 
import time
import shutil
       

def find_file_w_name_fragment(name_fragment, path):
    # return the first file with a given name_fragment in its file name
    for root, dirs, files in os.walk(path):
        for file in files:
            if name_fragment in file:
                return os.path.join(root, file)


def modify_and_run(oedi_download_folder, osw_path, openstudio_working_dir, cli_command,
                   unzip_folder, verbose):
    
    """
    Iterates through filenames, modifies a JSON entry, and executes OpenStudio workflows.
    
    Args:
      filenames: A list of filenames.
      osw_path: The path to the JSON file to modify.
      cli_command: The OpenStudio CLI command string.
    
    Raises:
      ValueError: If the JSON file cannot be loaded or modified.
      subprocess.CalledProcessError: If the OpenStudio CLI command fails.
    """
    
    print('\nGenerating EnergyPlus files..')
    
    ET.register_namespace("", "http://hpxmlonline.com/2019/10")
    ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
    ET.register_namespace("", 'http://hpxmlonline.com/2019/10')
    
    # get each folder (one per building), and the schedules and xml file in the foler
    root_dir = os.path.join(oedi_download_folder, unzip_folder)
    
    # generate building folders objects (holds folder, xml, csv paths)
    building_folders_objects = xml_modifier.get_folder_file_lists(root_dir)  

    startTime = time.time()
    for i, building_folder_obj in enumerate(building_folders_objects):
        try:
            # Load the JSON file
            with open(osw_path , 'r') as f:
                data = json.load(f)
        
            # Modify the entry with the building_folder_obj
            data['steps'][0]['arguments']['hpxml_path']  = building_folder_obj.xml  # Replace 'hpxml_path' with the xml filepath
        
            # Write the modified JSON back
            with open(osw_path, 'w') as f:
                json.dump(data, f, indent=4)
        
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
            
            # copy the generated .idf file to the correct output folder
            generated_idf = os.path.join(oedi_download_folder, 'run/in.idf')
            shutil.copy(generated_idf, building_folder_obj.folder)
            
            search_path = os.path.join(oedi_download_folder, "generated_files")

            # copy the generated schedules file to the correct output folder
            generated_schedule = find_file_w_name_fragment('schedule', search_path)
            shutil.copy(generated_schedule, building_folder_obj.folder)
            
            """
            TO DO: 
                point the .idf to the correct location for the schedules file we just copied
            """

        
        except (ValueError, json.JSONDecodeError) as e:
            raise Exception(f"Error modifying JSON for file {building_folder_obj.xml}: {e}")
      
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error running OpenStudio CLI for file {building_folder_obj.xml}: {e}")
        
        duration = (time.time() - startTime)/60
        rate = (i+1)/duration 
        est_time_min = (len(building_folders_objects)+1)/rate
        print('\r', str(i+1), '/', len(building_folders_objects), 'files generated.', 
              "Estimated time remaining", round(est_time_min - duration, 1), 
              'minutes.', 'Avg speed (sec/.idf):', round(1/rate*60, 1),  end='', flush=True)
    
    print('\nAll EnergyPlus files generated.\n')    
if __name__ == "__main__":
    modify_and_run()
    
    
    
    
    
    
    
    
    
    