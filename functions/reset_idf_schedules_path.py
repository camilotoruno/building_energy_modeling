#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 23:53:49 2024

@author: camilotoruno
"""

from eppy.modeleditor import IDF
import sys
import os 
import tqdm

def init_eppy(idf, **kwargs):
    # load the function's arguments 
    iddfile = kwargs.get('iddfile')
    pathnameto_eppy = kwargs.get('pathnameto_eppy') 
    
    if not os.path.exists(iddfile):
        raise FileNotFoundError('Correct the path to the .idd file. Find filepath to OpenStudio-3.4.0/EnergyPlus/Energy+.idd') 
    if not os.path.exists(pathnameto_eppy):
        raise FileNotFoundError('Correct the path to the eppy package. Example: <your python environment>/lib/python3.11/site-packages/epyy') 
    
    sys.path.append(pathnameto_eppy)
    IDF.setiddname(iddfile)  

    return IDF(idf)

def set_Schedules_Paths_Relative(buildings, **kwargs):

    for bldg in tqdm.tqdm(buildings, total=len(buildings), desc = 'Setting IDF schedules paths relative', smoothing=0.01):
        idf_obj = init_eppy(bldg.idf, **kwargs)

        # modify each schedule:File entry in an .idf
        for schedule in idf_obj.idfobjects['Schedule:File']:
            # remove all the filepath, leaving just the file name for relative file path instead of absolute file path
            schedule.File_Name = os.path.basename(bldg.schedules)

        idf_obj.save()          # overwrite original with modifications

def set_EnergyPlus_Simulation_Output(buildings, new_idf_options, **kwargs):

    # For each building 
    for bldg in tqdm.tqdm(buildings, total=len(buildings), desc = 'Setting IDF simulation outputs', smoothing=0.01):

        # load the IDF
        idf_obj = init_eppy(bldg.idf, **kwargs)

        for New_Outputs in new_idf_options:             # For all the new output types we want to add
            for options in New_Outputs['options']:      # for all the options for that field type
                
                # create a new output flag and set its values to the user supplied ones
                field = New_Outputs['field']
                if field == 'OutputControl:Files': new_flag = idf_obj.idfobjects[field][0] 

                else: new_flag = idf_obj.newidfobject(field)  # generate a new IDF output variable object

                for value, attrib in options.items():
                    if not hasattr(new_flag, attrib): raise RuntimeError(f'IDF file {field} does not have the attribute {attrib}')        
                    setattr(new_flag, attrib, value)         

        idf_obj.save()          # overwrite original with modifications