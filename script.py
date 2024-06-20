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
import pandas as pd

# import custom classes and functions
from functions import oedi_querying 
from functions import buildstock_filtering 
from functions import xml_modifier
from functions import modify_osw_and_run_openstudio 
from functions import argument_builder  
from functions import reset_idf_schedules_path
from functions import epw_finder

if __name__ == '__main__':
	multiprocessing.freeze_support()
	cwd = os.getcwd()   

	######################################### SET USER DEFINED ARGUMENTS ####################################################################
	filtering_arguments = {
		"buildstock_file": "baseline_metadata_only.csv",              # must be generated (derived) by resstock-euss.2022.1 version of ResStock
		# "buildstock_file": "baseline_metadata_only_example_subset.csv", # must be generated (derived) by resstock-euss.2022.1 version of ResStock

		"buildstock_folder": "/Users/camilotoruno/Documents/GitHub/building_energy_modeling",
		# "buildstock_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data"),

		# "buildstock_output_folder": os.path.join(os.path.sep, "Volumes", "seas-mtcraig", "EPWFromTGW"), 
		"buildstock_output_folder": "/Users/camilotoruno/Documents/local_research_data",
		# "buildstock_output_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data"), 

		"federal_poverty_levels": ['0-100%', '100-150%', '150-200%'],   # federal poverty levels to match format of buildstock_file
		"statistical_sample_size": 400,         # statistically representative sample size for a city. DOES NOT DEFINE CITY SIZE LIMIT.
												# Defines what we consider a statistically representative sample size, then scales the number of 
												# buildings to reach a proprtionally statistically representative sample by federal poverty level. 
												# See discussion in ASSET Lab
		"keep_cities": [
			"AZ, Phoenix",
			"CA, Los Angeles",
			# "CA, San Diego",
			# "CA, San Francisco",
			# "CO, Denver",
			"FL, Jacksonville",
			"FL, Miami",
			"IL, Chicago",
			# "IN, Indianapolis City Balance",
			# "KY, Louisville Jefferson County Metro Government Balance",
			"MD, Baltimore",
			"MI, Detroit",
			"MN, Duluth",
			# "MT, Billings",
			"NM, Albuquerque",
			"NY, New York",
			# "OH, Cleveland",
			"OK, Oklahoma City",
			"OR, Portland",
			"PA, Philadelphia",
			"TN, Memphis",
			"TX, Dallas",
			"TX, Houston",
			# "TX, San Antonio",
			# "WI, Milwaukee",
			],

		"exclude_cities": ['In another census Place', 'Not in a census Place']     # can be an empty list
		}

	oedi_querying_arguments = {
		"oedi_download_folder": filtering_arguments['buildstock_output_folder'],
		"bldg_download_folder_basename": 'buildings',                               # set as desired. Root name for folder of generated files
		"unzip": True,      # default False
		}

	epw_data = {
		# Mac Example
		# "weather_folder": "/Users/camilotoruno/Documents/local_research_data/TGWEPWs_trimmed",
		# "weather_folder": os.path.join(os.path.sep, "Users", "camilotoruno", "Documents", "ctoruno", "weather"), 

		# # Windows example
		# "weather_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data", "weather"),

		# Turbo location 
		"weather_folder": "/Volumes/seas-mtcraig/EPWFromTGW/TGWEPWs", 
		# "weather_folder": os.path.join(os.path.sep, "Z:", "EPWFromTGW", "TGWEPWs"), 

		"scenario_folders": [
                "historical_1980-2020",
                "rcp45cooler_2020-2060",
                # "rcp45cooler_2060-2100",
                # "rcp45hotter_2020-2060",
                # "rcp45hotter_2060-2100",
                "rcp85cooler_2020-2060",
                ### "rcp85cooler_2060-2100", - incomplete epw data 
                ], 
		}

	openstudio_workflow_arguments = {
		# Mac example
		"openstudio_path": "/usr/local/bin/openstudio",        # Set to local path. Requires openstudio version 3.4.0 in bin
		"openstudio_application_path": "/Applications/OpenStudio-3.4.0",  # set the OpenStudio application path to your downloaded copy. Requires OpenStudio 3.4.0

		# # Windows example 
		# "openstudio_path": os.path.join(os.path.sep, "openstudio-3.4.0", "bin", "openstudio.exe"),        # Set to local path. Requires openstudio version 3.4.0 in bin
		# "openstudio_application_path":  os.path.join(os.path.sep, "openstudio-3.4.0"),   # set the OpenStudio application path to your downloaded copy. Requires OpenStudio 3.4.0
		}
	

	idf_simulation_configuration = {
        'idf_configuration': "/Users/camilotoruno/Documents/GitHub/EnergyPlus-Python/simulation_output_configuration.idf",
	}

	misc_arguments = {
		# Set the location of your virtual environment 
		# Mac example
		"conda_venv_dir": "/Users/camilotoruno/anaconda3/envs/research",

		# # Windows example
		# "conda_venv_dir": os.path.join(os.path.sep, "Users", "ctoruno", "AppData", "Local", "anaconda3", "envs", "ResStock2EnergyPlus"),

		"verbose": False,
		"overwrite_output": False,
		"cwd": cwd,
		"max_cpu_load": 0.5      # must be in the range [0, 1]. The value 1 indidcates all CPU cores, 0 indicates 1 CPU core
		}
	
	# add calculated openstudio arguments to user arguments
	arguments = {**filtering_arguments, **oedi_querying_arguments, **epw_data, **openstudio_workflow_arguments, **idf_simulation_configuration, **misc_arguments}
	arguments = argument_builder.set_optional_args(arguments)
	arguments = argument_builder.set_calculated_args(arguments)
	argument_builder.file_check(**arguments)

	#################################### FILTER / LOAD BUILDSTOCK ########################################################
	startTime = time.time()

	# Filter the buildstock data by the desired characteristics 
	# capture a list of custom objects to track the folders, id and other useful info for each building
	buildstock_filtering.filtering(**arguments)

	#################################### BEGING PROCESSING DATA ########################################################
	    
    # create list of bldg objects for workflow
	buildstock = pd.read_csv(os.path.join(arguments["buildstock_output_folder"], arguments['bldg_download_folder_basename'], 'buildstock.csv'))
	building_objects_list = argument_builder.initialize_bldg_obj_ls(buildstock)

	# Find the weather files for each building and scenario and attach to each bldg in building objects list
	building_objects_list = epw_finder.weather_file_lookup(building_objects_list, **arguments)

	# # Query oedi for the required building zip file
	building_objects_list = oedi_querying.download_unzip(building_objects_list, **arguments)

	# if the files were unzipped, proceed with processing 
	if arguments["unzip"]: 
		#  Modify the xml files to allow openstudio workflow to run.
		building_objects_list = xml_modifier.modify_xml_files(building_objects_list, **arguments)
		
		# Call the openstudio command line interface to generate the .idf from .xml 
		building_objects_list = modify_osw_and_run_openstudio.modify_and_run(building_objects_list, **arguments)  #Rename to BuildstockGenerateIDFs

		# change the idf file to have a relative filepath for the schedule file
		# Add the desired output arguments for EnergyPlus simulations
		reset_idf_schedules_path.set_Schedules_Paths_Relative(building_objects_list, **arguments)
		reset_idf_schedules_path.set_EnergyPlus_Simulation_Output(building_objects_list, **arguments)

	# Convert elapsed time to hours, minutes, seconds
	elapsed_time = time.time() - startTime
	hours = int(elapsed_time // 3600)
	minutes = int((elapsed_time % 3600) // 60)
	seconds = int(elapsed_time % 60)
	print(f"\nWorkflow completed. {len(building_objects_list)} buildings generated in: {hours:02d}hr:{minutes:02d}min:{seconds:02d}sec \n")

