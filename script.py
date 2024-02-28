#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 23:02:00 2024

@author: camilotoruno
"""

"""
TO DO: 
    in the modify_osw_and_run_openstudio package 
        modify the generated .idf to point to the correct location for the schedules file we just copied
"""


import oedi_querying 
import buildstock_filtering 
import xml_modifier
import modify_osw_and_run_openstudio 
import os
from reset_idf_schedules_path import Set_Relative_Schedules_Filepath
from tqdm import tqdm
            
hpxml_measures_folder = "/Users/camilotoruno/resstock-euss.2022.1/resources/hpxml-measures"
openstudio_workflow_folder = os.path.join(hpxml_measures_folder, "workflow")
openstudio_workflow = "custom-run-hpxml.osw"
openstudio_workflow_file = os.path.join(openstudio_workflow_folder, openstudio_workflow)

args = {
        "output_buildstock_folder": hpxml_measures_folder,
        "buildstock_file": "baseline_metadata_only.csv",
        # "buildstock_file": "baseline_metadata_only_example_subset.csv",
        "buildstock_folder": "/Users/camilotoruno/anaconda3/envs/research/research_data/",
        "buildstock_output_file": "full_buildstock_24.02.27.csv",
        "buildstock_output_folder": hpxml_measures_folder,
        "federal_poverty_levels": ['0-100%', '100-150%', '150-200%'],
        "city_size_limit": 4,
        "keep_cities": [
                        # "AZ, Phoenix",
                        # "CA, Los Angeles",
                        # "CO, Denver",
                        # "FL, Orlando",
                        # "GA, Atlanta",
                        # "ID, Boise City",
                        # "IL, Chicago",
                        # "KS, Kansas City",
                        # "MA, Boston",
                        # "MI, Detroit",
                        # "MN, Minneapolis",
                        # "NE, Omaha",
                        # "NY, New York",
                        # "PA, Philadelphia",
                        "TX, Dallas"
                        ],
        
        "exclude_cities": ['In another census Place', 'Not in a census Place'],
                
        "unzipped_folders_folder": "test_unzipped_building_energy_models",
        "zipped_folders_folder": "test_zipped_building_energy_models",
        "oedi_download_folder": openstudio_workflow_folder,
        "oedi_filepath": "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/building_energy_models/upgrade=0/", 
        "bldg_download_folder_basename": 'Buildings', 
        
        "hpxml_measures_folder": hpxml_measures_folder,
        "osw_path": openstudio_workflow_file,
        "openstudio_workflow": openstudio_workflow,
        "openstudio_path": "/usr/local/bin/openstudio",
        "openstudio_workflow_folder": openstudio_workflow_folder,
        "openstudio_working_dir": hpxml_measures_folder,
        
        "iddfile": "/Applications/OpenStudio-3.4.0/EnergyPlus/Energy+.idd",
        "pathnameto_eppy": "/Users/camilotoruno/anaconda3/envs/research/lib/python3.11/site-packages/eppy",
            
        "unzip": True,
        }

# set default optional arguments
if 'save_buildstock' not in args.keys(): args['save_buildstock'] = True
if 'verbose' not in args.keys(): args["verbose"] = False
if 'unzip' not in args.keys(): args['unzip'] = False

# filter the buildstock data by the desired characteristics 
building_objects_list = buildstock_filtering.filtering(**args)

# query oedi for the required building zip file
building_objects_list = oedi_querying.download_unzip(building_objects_list, **args)

if args["unzip"]: 
    #  modify the xml files to allow openstudio workflow to run 
    building_objects_list = xml_modifier.modify_xml_files(building_objects_list)
    
    # call the openstudi command line interface to generate the .idf from .xml 
    building_objects_list = modify_osw_and_run_openstudio.modify_and_run(building_objects_list, **args)
        
    # Reset the .idf files' schedules file path to be relative (assumes schedules in same folder as idf)
    Set_Relative_Schedules_Filepath(building_objects_list, **args)
    
    # remove original files, keep generated ones        
    # Use tqdm to iterate with a progress bar
    for bldg in tqdm(building_objects_list, desc="Removing original files", smoothing=0.01): # smoothing near avg time est
        os.remove(bldg.schedules)   # remove the original schedules file (keeping the generated one)
        os.remove(bldg.xml)         # remove the original .xml file (keeping the modified one)

print('\nWorkflow completed')    
