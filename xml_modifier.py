#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:14:03 2024

This script takes an xml file from OEDI and the schedules.csv file and modifies 
the .xml file to reference the right schedules.csv file location 

It also removes the EmissionsScenario tag from the .xml file to avoid errors from 
not being able to find the associated / required files for emissions schenarios

@author: camilotoruno
"""

import xml.etree.ElementTree as ET
import os 

def change_attrib_text(new_text, root, attrib):
    """Change the schedules.csv file to point to the downloaded one for a building """
    for element in root.iter():
        if attrib in element.tag:
            element.text = new_text
            

def remove_tags(parent, tag_name):
    """Recursively removes all tags with the given name from a parent element."""
    for child in parent:
        if tag_name in child.tag:
            parent.remove(child)
        else:
            remove_tags(child, tag_name)  


def modify_xml(building_folder):
    tree = ET.parse(building_folder.xml)
    root = tree.getroot()
    
    remove_tags(root, 'EmissionsScenarios')  # Replace with the tag name you want to remove
    change_attrib_text(building_folder.csv, root, attrib='SchedulesFilePath')
    change_attrib_text(new_text="../../../weather/G5100330.epw", 
                        root=root, 
                        attrib='EPWFilePath') # point to arbitrary epw file I have (required for workflow, not for .idf)
    
    tree.write(os.path.join(building_folder.folder, "modified_in.xml"), 
               encoding="UTF-8", xml_declaration=True)
    

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

for building_folder in building_folders:
    modify_xml(building_folder)
    
print('Modified', len(building_folders), 'files')

