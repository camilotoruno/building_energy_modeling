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
import reset_idf_schedules_path
import epw_finder

if __name__ == '__main__':
	multiprocessing.freeze_support()

	######################################### SET USER DEFINED ARGUMENTS ####################################################################
	filtering_arguments = {
		# "buildstock_file": "baseline_metadata_only.csv",              # must be generated (derived) by resstock-euss.2022.1 version of ResStock
		"buildstock_file": "baseline_metadata_only_example_subset.csv", # must be generated (derived) by resstock-euss.2022.1 version of ResStock
		"buildstock_folder": os.path.join(os.path.sep, "Users", "camilotoruno", "Documents", "GitHub", "building_energy_modeling"),
		# "buildstock_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data"),

		"buildstock_output_file": "test_buildstock.csv",
		"bldg_download_folder_basename": 'testing_run',                               # set as desired. Root name for folder of generated files

		# "buildstock_output_folder": os.path.join(os.path.sep, "Volumes", "seas-mtcraig", "EPWFromTGW"), 
		"buildstock_output_folder": os.path.join(os.path.sep, "Users", "camilotoruno", "Documents", "local_research_data"), 
		# "buildstock_output_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data"), 

		"federal_poverty_levels": ['0-100%', '100-150%', '150-200%'],   # federal poverty levels to match format of buildstock_file
		"statistical_sample_size": 400,         # statistically representative sample size for a city. DOES NOT DEFINE CITY SIZE LIMIT.
												# Defines what we consider a statistically representative sample size, then scales the number of 
												# buildings to reach a proprtionally statistically representative sample by federal poverty level. 
												# See discussion in ASSET Lab
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
		"unzip": True,      # default False
		}

	epw_data = {
		# Mac Example
		"weather_folder": "/Users/camilotoruno/Documents/GitHub/EnergyPlus-Python/TGWEPWs_trimmed",
		# "weather_folder": os.path.join(os.path.sep, "Users", "camilotoruno", "Documents", "ctoruno", "weather"), 

		# # Windows example
		# "weather_folder": os.path.join(os.path.sep, "Users", "ctoruno", "Documents", "local_research_data", "weather"),

		# Turbo location 
		# "weather_folder": os.path.join(os.path.sep, "Volumes", "seas-mtcraig-1", "EPWFromTGW", "TGWEPWs"), 
		# "weather_folder": os.path.join(os.path.sep, "Z:", "EPWFromTGW", "TGWEPWs"), 
		
		"scenario_folders": ["historical_1980-2020", "rcp45cooler_2020-2060"]#, "rcp45hotter_2020-2060", "rcp85cooler_2020-2060"],
		}

	openstudio_workflow_arguments = {
		# Mac example
		"openstudio_path": os.path.join(os.path.sep, "usr", "local", "bin", "openstudio"),        # Set to local path. Requires openstudio version 3.4.0 in bin
		"openstudio_application_path": os.path.join(os.path.sep, "Applications", "OpenStudio-3.4.0"),  # set the OpenStudio application path to your downloaded copy. Requires OpenStudio 3.4.0

		# # Windows example 
		# "openstudio_path": os.path.join(os.path.sep, "openstudio-3.4.0", "bin", "openstudio.exe"),        # Set to local path. Requires openstudio version 3.4.0 in bin
		# "openstudio_application_path":  os.path.join(os.path.sep, "openstudio-3.4.0"),   # set the OpenStudio application path to your downloaded copy. Requires OpenStudio 3.4.0
		}
	

	# Define the desired output file settings
	new_Output_Control_Files = {
		"field":'OutputControl:Files',
		"options": [
			# turn on (OpenStudio defaults of no)
			{'Yes': 'Output_MTR'},     

			{'Yes': 'Output_ESO'},      

			# turn off (OpenStudio defaults of yes)
			{'No': 'Output_Tabular'},   

			{'No': 'Output_SQLite'},     

			{'No': 'Output_JSON'},
			]
		}
	

	new_Output_Variables = {
		"field": "Output:Variable", 
		"options": [
			{"*": "Key_Value",
			"Zone Air Temperature": "Variable_Name",
			"Hourly": "Reporting_Frequency"},

			{"*": "Key_Value",
			"Site Outdoor Air Wetbulb Temperature": "Variable_Name",
			"Timestep": "Reporting_Frequency"},

			{"*": "Key_Value",
			"Zone Air Relative Humidity": "Variable_Name",
			"Daily": "Reporting_Frequency"},

			{"*": "Key_Value",
			"Zone Air Relative Humidity": "Variable_Name",
			"Hourly": "Reporting_Frequency"},

			{"*": "Key_Value",
			"Site Outdoor Air Drybulb Temperature": "Variable_Name",
			"Monthly": "Reporting_Frequency"}
				]
		}

	new_Output_Meters = {
		"field": "Output:Meter", 
		"options": [
			{"Electricity:Facility": "Key_Name",
			"Timestep": "Reporting_Frequency"},

			{"NaturalGas:Facility": "Key_Name",
			"Timestep": "Reporting_Frequency"},

			{"DistrictCooling:Facility": "Key_Name",
			"Timestep": "Reporting_Frequency"},

			{"DistrictHeatingWater:Facility:": "Key_Name",
			"Timestep": "Reporting_Frequency"}
			]
		}

	new_Outputs_MeterFileOnly = {
		"field": "Output:Meter:MeterFileOnly", 
		"options": [
			{"NaturalGas:Facility": "Key_Name",
			"Daily": "Reporting_Frequency"},

			{"Electricity:Facility": "Key_Name",
			"Timestep": "Reporting_Frequency"},

			{"Electricity:Facility": "Key_Name",
			"Daily": "Reporting_Frequency"}
			]
		}

	misc_arguments = {
		# set the location of your virtual environment 
		# Mac example
		"conda_venv_dir": os.path.join(os.path.sep, "Users", "camilotoruno", "anaconda3", "envs", "research"),

		# # Windows example
		# "conda_venv_dir": os.path.join(os.path.sep, "Users", "ctoruno", "AppData", "Local", "anaconda3", "envs", "ResStock2EnergyPlus"),

		"verbose": False,
		"overwrite_output": False,
		"cwd": os.getcwd(), 
		"max_cpu_load": 0.99      # must be in the range [0, 1]. The value 1 indidcates all CPU cores, 0 indicates 1 CPU core
		}
	
	# add calculated openstudio arguments to user arguments
	arguments = {**filtering_arguments, **oedi_querying_arguments, **epw_data, **openstudio_workflow_arguments, **misc_arguments}
	arguments = argument_builder.set_optional_args(arguments)
	arguments = argument_builder.set_calculated_args(arguments)
	argument_builder.file_check(**arguments)
	new_idf_options = [new_Output_Control_Files, new_Output_Variables, new_Output_Meters, new_Outputs_MeterFileOnly]

	#################################### BEGING PROCESSING DATA ########################################################
	startTime = time.time()

	# Filter the buildstock data by the desired characteristics 
	# capture a list of custom objects to track the folders, id and other useful info for each building
	building_objects_list = buildstock_filtering.filtering(**arguments)

	# Find the weather files for each building and scenario and attach to each bldg in building objects list
	building_objects_list = epw_finder.weather_file_lookup(building_objects_list, **arguments)

	# Query oedi for the required building zip file
	building_objects_list = oedi_querying.download_unzip(building_objects_list, **arguments)

	# if the files were unzipped, proceed with processing 
	if arguments["unzip"]: 
		#  Modify the xml files to allow openstudio workflow to run.
		building_objects_list = xml_modifier.modify_xml_files(building_objects_list, **arguments)
		
		# Call the openstudio command line interface to generate the .idf from .xml 
		building_objects_list = modify_osw_and_run_openstudio.modify_and_run(building_objects_list, **arguments)

		# change the idf file to have a relative filepath for the schedule file
		# Add the desired output arguments for EnergyPlus simulations
		reset_idf_schedules_path.set_Schedules_Paths_Relative(building_objects_list, **arguments)
		reset_idf_schedules_path.set_EnergyPlus_Simulation_Output(building_objects_list, new_idf_options, **arguments)

	# Convert elapsed time to hours, minutes, seconds
	elapsed_time = time.time() - startTime
	hours = int(elapsed_time // 3600)
	minutes = int((elapsed_time % 3600) // 60)
	seconds = int(elapsed_time % 60)
	print(f"\nWorkflow completed. {len(building_objects_list)} buildings generated in: {hours:02d}hr:{minutes:02d}min:{seconds:02d}sec \n")

