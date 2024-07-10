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
from copy import copy
import math
import multiprocessing

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


def worker(job):
        bldg = job
        kwargs = job.kwargs
        idf_obj = init_eppy(bldg.idf, **kwargs)
        configuration = init_eppy(kwargs.get('idf_configuration'), **kwargs)

        if bldg.schedules == None: 
            raise RuntimeError(f"Bldg has None schedules. {bldg.weather_scenario} / {bldg.city} / Bldg {bldg.id}")

        # modify each schedule:File entry in an .idf
        for schedule in idf_obj.idfobjects['Schedule:File']:
            schedule.File_Name = str(bldg.schedules)   # NOTE: Changed to use absolute file path 

        # load the IDF
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
                try:   # The building IDF may not have the field
                    idf_obj.idfobjects[field] = configuration.idfobjects[field]  
                except:  # if the field isnt in the bldg file, add it then set its value 
                    if kwargs.get('verbose'): print(f'IDF does not have field {field}')
                    # new_flag = idf_obj.newidfobject(field)
                    idf_obj.idfobjects[field] = configuration.idfobjects[field]

        idf_obj.save()          # overwrite original with modifications

        
def set_Schedules_and_Output(buildings, **kwargs):

    # assign arguments for job list
    jobs = []
    for bldg in buildings: 
        job = copy(bldg)
        job.kwargs = kwargs
        jobs.append(job)

    # Setup the job pool
    # at least one CPU core, up to max_cpu_load * num_cpu_cores, no more cores than jobs
    num_cpus = max(min( math.floor( kwargs.get('max_cpu_load') * multiprocessing.cpu_count()), len(jobs)), 1)    
    pool = multiprocessing.Pool(processes=num_cpus)
    no_jobs = len(jobs)
    
    # Execute the job pool and track progress with tqdm progress bar
    print(f'Setting {len(jobs)} IDF schedules paths using {num_cpus} CPU cores')
    for _ in tqdm.tqdm(pool.imap_unordered(worker, jobs), total=no_jobs, desc="Setting IDF schedules and Simulation Configuration", smoothing=0.01):
        pass


        