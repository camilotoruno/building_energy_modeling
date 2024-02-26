#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 23:53:49 2024

@author: camilotoruno
"""

from eppy.modeleditor import IDF
import sys
import os 
from xml_modifier import get_bldg_objs_list
import argparse

def set_idf_schedule_path(idf_filename):
    # function removes all path besides filename. Requires that all downstream 
    # proceessing has idf and schedules in the same folder for a given building 
    
    idf_obj = IDF(idf_filename)
    
    # modify each schedule:File entry in an .idf
    for schedule in idf_obj.idfobjects['Schedule:File']:
        # remove all the filepath, leaving just the file name for relative file path
        # instead of absolute file path
        schedule.File_Name = schedule.File_Name.split('/')[-1]
        
    # overwrite original with modifications
    idf_obj.save()


def Set_Relative_Schedules_Filepath(**kwargs):
    print('Resetting scheduels file path in .idf files...')
    # load the function's arguments 
    iddfile = kwargs.get('iddfile')
    pathnameto_eppy = kwargs.get('pathnameto_eppy') 
    unzipped_buildings_folder = kwargs.get('unzipped_buildings_folder')
    openstudio_workflow_dir = kwargs.get('openstudio_workflow_dir')
    
    if not os.path.exists(iddfile):
        raise FileNotFoundError('Correct the path to the .idd file. Find filepath to OpenStudio-3.4.0/EnergyPlus/Energy+.idd') 
    if not os.path.exists(pathnameto_eppy):
        raise FileNotFoundError('Correct the path to the eppy package. Example: <your python environment>/lib/python3.11/site-packages/epyy') 
    
    sys.path.append(pathnameto_eppy)
    IDF.setiddname(iddfile)

    building_objects = get_bldg_objs_list(os.path.join(openstudio_workflow_dir, unzipped_buildings_folder))
    
    for building in building_objects:
        set_idf_schedule_path(building.idf)
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set relative schedules.csv file path for all idf files")

    # Add arguments with appropriate types and help messages
    parser.add_argument("iddfile", type=str, help="Buildstock CSV file")
    parser.add_argument("pathnameto_eppy", type=str, help="Absolute path to the buildstock folder")
    parser.add_argument("unzipped_buildings_folder", type=str, help="Path to the unzipped building_folder")

    args = parser.parse_args()

    Set_Relative_Schedules_Filepath(**vars(args)) 
    
    
    