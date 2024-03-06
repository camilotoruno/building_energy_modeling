#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 23:02:00 2024
@author: camilotoruno

Workflow script that acts as a coordinator of functions needed to generate .idf building files from
ResStock buildstock data. 
"""

import os
from tqdm import tqdm

# import custom classes and functions
import oedi_querying 
import buildstock_filtering 
import xml_modifier
import modify_osw_and_run_openstudio 
from argument_builder import argument_builder  
from reset_idf_schedules_path import Set_Relative_Schedules_Filepath


cwd = os.getcwd()   
openstudio_args = argument_builder.set_openstudio_args(cwd)

# Set user defined arguments 
filtering_arguments = {
        "buildstock_file": "baseline_metadata_only.csv",              # must be generated (derived) by resstock-euss.2022.1 version of ResStock
        # "buildstock_file": "baseline_metadata_only_example_subset.csv", # must be generated (derived) by resstock-euss.2022.1 version of ResStock
        
        "buildstock_folder": os.path.join(os.path.sep, "Users", "camilotoruno", "Documents", "GitHub", "building_energy_modeling"),
        # "buildstock_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "research_data"),

        "buildstock_output_file": "full_buildstock_24.02.27.csv",
        "buildstock_output_folder": cwd, 
        "federal_poverty_levels": ['0-100%', '100-150%', '150-200%'],   # federal poverty levels to match format of buildstock_file
        "city_size_limit": 1,                                           # max number of houses per city
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
        "exclude_cities": ['In another census Place', 'Not in a census Place']     # can be an empty list
        }

oedi_querying_arguments = {
        "oedi_download_folder": filtering_arguments['buildstock_folder'],
        "bldg_download_folder_basename": 'Buildings',                               # set as desired. Root name for folder of generated files
        "unzip": True,      # default False
        }

openstudio_workflow_arguments = {
        # Mac example
        "openstudio_path": os.path.join(os.path.sep, "usr", "local", "bin", "openstudio"),        # Set to local path. Requires openstudio version 3.4.0 in bin
        # set the OpenStudio application path to your downloaded copy. Requires OpenStudio 3.4.0
        "openstudio_application_path": os.path.join(os.path.sep, "Applications", "OpenStudio-3.4.0"),

        # # Windows example 
        # "openstudio_path": os.path.join(os.path.sep, "openstudio-3.4.0", "bin", "openstudio.exe"),        # Set to local path. Requires openstudio version 3.4.0 in bin
        # # set the OpenStudio application path to your downloaded copy. Requires OpenStudio 3.4.0
        # "openstudio_application_path":  os.path.join(os.path.sep, "openstudio-3.4.0"),
        }

misc_arguments = {
        # set the location of your virtual environment 
        # Mac example
        "conda_venv_dir": os.path.join(os.path.sep, "Users", "camilotoruno", "anaconda3", "envs", "research"),

        # # Windows example
        # "conda_venv_dir": os.path.join(os.path.sep, "Users", "ctoruno", "AppData", "Local", "anaconda3", "envs", "ResStock2EnergyPlus"),
        }
# add calculated openstudio arguments to user arguments
arguments = {**filtering_arguments, **oedi_querying_arguments, **openstudio_workflow_arguments, **misc_arguments}
arguments.update(openstudio_args)   # add generated openstudio args to user arguments 

# set optional and calculated arguments 
arguments = argument_builder.set_optional_args(arguments)
arguments = argument_builder.set_calculated_args(arguments)


#################################### BEGING PROCESSING DATA ########################################################

# Filter the buildstock data by the desired characteristics 
# capture a list of custom objects to track the folders, id and other useful info for each building
building_objects_list = buildstock_filtering.filtering(**arguments)

# Query oedi for the required building zip file
building_objects_list = oedi_querying.download_unzip(building_objects_list, **arguments)

# if the files were unzipped, proceed with processing 
if arguments["unzip"]: 
    #  Modify the xml files to allow openstudio workflow to run 
    building_objects_list = xml_modifier.modify_xml_files(building_objects_list)
    
    # Call the openstudi command line interface to generate the .idf from .xml 
    building_objects_list = modify_osw_and_run_openstudio.modify_and_run(building_objects_list, **arguments)
        
    # Reset the .idf files' schedules file path to be relative (assumes schedules in same folder as idf)
    Set_Relative_Schedules_Filepath(building_objects_list, **arguments)
    
    # Remove original files, keep generated ones        
    # Use tqdm to iterate with a progress bar
    for bldg in tqdm(building_objects_list, desc="Removing original files", smoothing=0.01): # smoothing near avg time est
        os.remove(bldg.schedules)   # remove the original schedules file (keeping the generated one)
        os.remove(bldg.xml)         # remove the original .xml file (keeping the modified one)

print('\nWorkflow completed\n')    
