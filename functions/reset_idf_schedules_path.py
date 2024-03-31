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

def set_EnergyPlus_Simulation_Output(buildings, **kwargs):

    # For each building 
    for bldg in tqdm.tqdm(buildings, total=len(buildings), desc = 'Setting IDF simulation outputs', smoothing=0.01):

        # load the IDF
        idf_obj = init_eppy(bldg.idf, **kwargs)
        configuration = init_eppy(kwargs.get('idf_configuration'), **kwargs)
        # print(f'Configuration file: {configuration}')

        # raise RuntimeError
        # print("\n\n")
        # print(configuration.idfobjects)
        # # print("\n\n")
        # print(dir(configuration), '\n\n')
        # # print(f"type(configuration.idfobjects): {type(configuration.idfobjects)} \n\n")
        
        # print('idf_obj.getiddgroupdict()')
        # for key, value in idf_obj.getiddgroupdict().items():
        #     print(f'key, value: {key} \t\t {value}\n\n')

        # print('\n\n\n\n\n\n ########################################################################################################## \n\n\n\n\n\n\n\n')
        # print('configuration.getiddgroupdict()')
        # for key, value in configuration.getiddgroupdict().items():
        #     print(f'key, value: {key} \t\t {value}\n\n')


        # print(f"getiddgroupdict: {configuration.getiddgroupdict()}")
        for field in configuration.idfobjects:

            # if the configuration file IDF object has instances of the field type (len > 0)                
            if len(configuration.idfobjects[field]) > 0:
                try: 
                    idf_obj.idfobjects[field] = configuration.idfobjects[field]    # The building IDF may not have the field
                except:           
                    # if the field isnt in the bldg file, add it then set its value 
                    print(f'IDF does not have field {field}')
                    new_flag = idf_obj.newidfobject(field)
                    idf_obj.idfobjects[field] = configuration.idfobjects[field]

        # raise RuntimeError
        idf_obj.save()          # overwrite original with modifications