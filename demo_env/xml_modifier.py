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


def modify_xml(building_obj):
    tree = ET.parse(building_obj.xml)
    root = tree.getroot()
    
    remove_tags(root, 'EmissionsScenarios')  # Replace with the tag name you want to remove
    change_attrib_text(building_obj.schedules, root, attrib='SchedulesFilePath')
    change_attrib_text(new_text="../../../weather/G5100330.epw", 
                        root=root, 
                        attrib='EPWFilePath') # point to arbitrary epw file I have (required for workflow, not for .idf)
    
    # write the modified building xml file 
    modified_xml = os.path.join(building_obj.folder, "modified_in.xml")
    tree.write(modified_xml, encoding="UTF-8", xml_declaration=True)
    
    return modified_xml


def modify_xml_files(bldg_obj_list):
    
    ET.register_namespace("", "http://hpxmlonline.com/2019/10")
    ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
    ET.register_namespace("", 'http://hpxmlonline.com/2019/10')    
            
    for i in range(len(bldg_obj_list)):
        bldg_obj_list[i].modified_xml = modify_xml(bldg_obj_list[i])
        
    print('\nModified', len(bldg_obj_list), 'hpxml (.xml) files')

    return bldg_obj_list
