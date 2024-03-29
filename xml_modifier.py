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
from tqdm import tqdm

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


def modify_xml_files(buildings, **kwargs):
    
    ET.register_namespace("", "http://hpxmlonline.com/2019/10")
    ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
    ET.register_namespace("", 'http://hpxmlonline.com/2019/10')    
    
    # Use tqdm to iterate with a progress bar
    for bldg in tqdm(buildings, desc="Modifying building .xml files", smoothing=0.01): # smoothing near avg time est

        # if the file doesn't exist or we're okay with overwriting 
        if kwargs.get('overwrite_output') or not(os.path.exists(bldg.modified_xml)):
            # modify and write the (hp)xml file out

            if os.path.exists(bldg.modified_xml): 
                if kwargs.get('verbose'): print(f"bldg.modified_xml {bldg.modified_xml} exists and is being overwritten")
                os.remove(bldg.modified_xml)

            if kwargs.get('verbose'): 
                print(f'\n\tInput xml file: {bldg.xml}')
                print('\tModified XML file exists and being overwritten:', bldg.modified_xml)

            tree = ET.parse(bldg.xml)
            root = tree.getroot()
            
            remove_tags(root, 'EmissionsScenarios')  
            change_attrib_text(bldg.schedules, root, attrib='SchedulesFilePath')
            change_attrib_text(# new_text="../../../weather/G5100330.epw", 
                                new_text = bldg.epw, 
                                root=root, 
                                attrib='EPWFilePath') 
            
            # write the modified building xml file 
            tree.write(bldg.modified_xml, encoding="UTF-8", xml_declaration=True)

    return buildings
