#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 23:02:00 2024
@author: camilotoruno

Workflow script that acts as a coordinator of functions needed to generate .idf building files from
ResStock buildstock data. 
"""

import os
import multiprocessing
import time 

# import custom classes and functions
import oedi_querying 
import buildstock_filtering 
import xml_modifier
import modify_osw_and_run_openstudio 
import argument_builder  
from reset_idf_schedules_path import Set_Relative_Schedules_Filepath
import epw_finder

if __name__ == '__main__':
        multiprocessing.freeze_support()
        cwd = os.getcwd()   

        ######################################### SET USER DEFINED ARGUMENTS ####################################################################
        filtering_arguments = {
                "buildstock_file": "baseline_metadata_only.csv",              # must be generated (derived) by resstock-euss.2022.1 version of ResStock
                # "buildstock_file": "baseline_metadata_only_example_subset.csv", # must be generated (derived) by resstock-euss.2022.1 version of ResStock
                "buildstock_output_file": "Dallas_buildstock_24.03.19.csv",

                "buildstock_folder": os.path.join(os.path.sep, "Users", "camilotoruno", "Documents", "GitHub", "building_energy_modeling"),
                # "buildstock_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data"),

                # "buildstock_output_folder": os.path.join(os.path.sep, "Volumes", "seas-mtcraig", "EPWFromTGW"), 
                "buildstock_output_folder": os.path.join(os.path.sep, "Users", "camilotoruno", "Documents", "local_research_data"), 
                # "buildstock_output_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data"), 

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
                "oedi_download_folder": filtering_arguments['buildstock_output_folder'],
                "bldg_download_folder_basename": 'Buildings',                               # set as desired. Root name for folder of generated files
                "unzip": True,      # default False
                }

        epw_data = {
                # Mac Example
                # "weather_folder": "/Users/camilotoruno/Documents/ctoruno/TGWEPWs",
                # "weather_folder": os.path.join(os.path.sep, "Users", "camilotoruno", "Documents", "ctoruno", "weather"), 

                # # Windows example
                # "weather_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data", "weather"),

                # Turbo location 
                "weather_folder": os.path.join(os.path.sep, "Volumes", "seas-mtcraig", "EPWFromTGW", "TGWEPWs"), 
                # "weather_folder": os.path.join(os.path.sep, "Z:", "EPWFromTGW", "TGWEPWs"), 

                "scenario_folders": ["historical_1980-2020"]#, "rcp45cooler_2020-2060", "rcp45hotter_2020-2060", "rcp85cooler_2020-2060"],
                # "scenario_folders": ["Historical"]
                }

        openstudio_workflow_arguments = {
                # Mac example
                "openstudio_path": os.path.join(os.path.sep, "usr", "local", "bin", "openstudio"),        # Set to local path. Requires openstudio version 3.4.0 in bin
                "openstudio_application_path": os.path.join(os.path.sep, "Applications", "OpenStudio-3.4.0"),  # set the OpenStudio application path to your downloaded copy. Requires OpenStudio 3.4.0

                # # Windows example 
                # "openstudio_path": os.path.join(os.path.sep, "openstudio-3.4.0", "bin", "openstudio.exe"),        # Set to local path. Requires openstudio version 3.4.0 in bin
                # "openstudio_application_path":  os.path.join(os.path.sep, "openstudio-3.4.0"),   # set the OpenStudio application path to your downloaded copy. Requires OpenStudio 3.4.0
                }

        misc_arguments = {
                # set the location of your virtual environment 
                # Mac example
                "conda_venv_dir": os.path.join(os.path.sep, "Users", "camilotoruno", "anaconda3", "envs", "research"),

                # # Windows example
                # "conda_venv_dir": os.path.join(os.path.sep, "Users", "ctoruno", "AppData", "Local", "anaconda3", "envs", "ResStock2EnergyPlus"),

                "verbose": False,
                "overwrite_output": False,

                "cwd": cwd,
                "max_cpu_load": 0.99      # must be in the range [0, 1]. The value 1 indidcates all CPU cores, 0 indicates 1 CPU core
                }
        
        # add calculated openstudio arguments to user arguments
        arguments = {**filtering_arguments, **oedi_querying_arguments, **epw_data, **openstudio_workflow_arguments, **misc_arguments}
        arguments = argument_builder.set_optional_args(arguments)
        arguments = argument_builder.set_calculated_args(arguments)
        argument_builder.file_check(**arguments)

        #################################### BEGING PROCESSING DATA ########################################################

        # Filter the buildstock data by the desired characteristics 
        # capture a list of custom objects to track the folders, id and other useful info for each building
        building_objects_list = buildstock_filtering.filtering(**arguments)

        # Query oedi for the required building zip file
        startTime = time.time()
        building_objects_list = oedi_querying.download_unzip(building_objects_list, **arguments)

        # Find the weather files for each building and scenario and attach to each bldg in building objects list
        building_objects_list = epw_finder.weather_file_lookup(building_objects_list, **arguments)

        # if the files were unzipped, proceed with processing 
        if arguments["unzip"]: 
                #  Modify the xml files to allow openstudio workflow to run.
                building_objects_list = xml_modifier.modify_xml_files(building_objects_list, **arguments)

                # Call the openstudio command line interface to generate the .idf from .xml 
                building_objects_list = modify_osw_and_run_openstudio.modify_and_run(building_objects_list, **arguments)

        # Convert elapsed time to hours, minutes, seconds
        elapsed_time = time.time() - startTime
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        print(f"\nWorkflow completed. {len(building_objects_list)} buildings generated in: {hours:02d}hr:{minutes:02d}min:{seconds:02d}sec \n")

