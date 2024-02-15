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

def get_folder_file_lists(root_dir):
    """
    Gets a list of files in each subfolder within the given directory.
    
    Args:
      root_dir: The path to the starting directory.
    
    Returns:
      A dictionary where keys are folder paths and values are lists of files in that folder.
    """
    
    folders = []
    i = 0
    for folder in os.listdir(root_dir):
        if os.path.isdir(os.path.join(root_dir, folder)):
            full_path = os.path.join(root_dir, folder)
            folders.append( BuildingFolder(full_path) )
            for file in os.listdir(full_path):
                if "schedules.csv" in file:
                    folders[i].set_csv(os.path.join(full_path, file))
                elif "in.xml" in file:
                    folders[i].set_xml(os.path.join(full_path, file))
            i += 1
            
    return folders
        

class BuildingFolder:
    """
    Represents a custom object with folder, schedule, and xml attributes.
    """
    def __init__(self, folder):
        self.folder = folder
        self.csv = None
        self.xml = None
    
    def set_csv(self, csv):
        self.csv = csv
    
    def set_xml(self, xml):
        self.xml = xml


ET.register_namespace("", "http://hpxmlonline.com/2019/10")
ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
ET.register_namespace("", 'http://hpxmlonline.com/2019/10')

download_folder = "/Users/camilotoruno/anaconda3/envs/research/research_data/"
unzip_folder = "building_energy_models/"


# get each folder (one per building), and the schedules and xml file in the foler
root_dir = os.path.join(download_folder, unzip_folder)
building_folders = get_folder_file_lists(root_dir)

# for building_folder in building_folders:
#     modify_xml(building_folder)
    
# print('Modified', len(building_folders), 'files')



def modify_osw_and_run_openstudio(building_folders, json_path, cli_command):
    """
    Iterates through filenames, modifies a JSON entry, and executes OpenStudio workflows.
    
    Args:
      filenames: A list of filenames.
      json_path: The path to the JSON file to modify.
      cli_command: The OpenStudio CLI command string.
    
    Raises:
      ValueError: If the JSON file cannot be loaded or modified.
      subprocess.CalledProcessError: If the OpenStudio CLI command fails.
    """

    for building_folder in building_folders:
        try:
            # Load the JSON file
            with open(json_path, 'r') as f:
                data = json.load(f)
        
            # Modify the entry with the building_folder
            data['steps'][0]['arguments']['hpxml_path']  = building_folder.xml  # Replace 'hpxml_path' with the xml filepath
        
            # Write the modified JSON back
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
        
            # Execute the OpenStudio CLI command
            # subprocess.run(cli_command.format(building_folder), check=True)
        
            print(f"Successfully processed file: {building_folder.xml}")
      
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error modifying JSON for file {building_folder.xml}: {e}")
      
        except subprocess.CalledProcessError as e:
            print(f"Error running OpenStudio CLI for file {building_folder.xml}: {e}")

# Example usage
json_path = "/Users/camilotoruno/resstock-euss.2022.1/resources/hpxml-measures/workflow/custom-run-hpxml.osw"
cli_command = "openstudio run --workflow workflow/template-run-hpxml.osw --measures_only"

modify_osw_and_run_openstudio(building_folders, json_path, cli_command)

