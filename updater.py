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
from pathlib import Path

import xml.etree.ElementTree as ET


# import custom classes and functions
from functions import oedi_querying 
from functions import buildstock_filtering 
from functions import xml_modifier
from functions import modify_osw_and_run_openstudio 
from functions import argument_builder  
from functions import reset_idf_schedules_path
from functions import epw_finder
import shutil

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
			"CA, San Diego",
			"CA, San Francisco",
			# "CO, Denver",     # not in weather folder
			"FL, Jacksonville",
			"FL, Miami",
			"IL, Chicago",
			# "IN, Indianapolis",
			# "KY, Louisville Jefferson County Metro Government Balance",   # not in weather folder
			"MD, Baltimore",
			"MI, Detroit",
			"MN, Duluth",
			"MT, Billings",



			# "NM, Albuquerque",
			# "NY, New York",
			# "OH, Cleveland",
			# "OK, Oklahoma City",
			# "OR, Portland",
			# "PA, Philadelphia",
			# "TN, Memphis",
			# "TX, Dallas",
			# "TX, Houston",
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
                "rcp45hotter_2020-2060",
                # "rcp45hotter_2060-2100",
                "rcp85cooler_2020-2060",
                ### "rcp85cooler_2060-2100", - incomplete epw data 
                ], 
		}

	openstudio_workflow_arguments = {
		# Mac example
		"openstudio_path": "/Applications/OpenStudio-3.4.0/bin/openstudio",        # Set to local path. Requires openstudio version 3.4.0 in bin
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
		"max_cpu_load": 6/12,      # must be in the range [0, 1]. The value 1 indidcates all CPU cores, 0 indicates 1 CPU core
		}
	
	arguments = {**filtering_arguments, **oedi_querying_arguments, **epw_data, **openstudio_workflow_arguments, **idf_simulation_configuration, **misc_arguments}   	# add calculated openstudio arguments to user arguments
	arguments = argument_builder.set_optional_args(arguments)
	arguments = argument_builder.set_calculated_args(arguments)
	argument_builder.file_check(**arguments)

	####################################  ########################################################
	startTime = time.time()

	configuration = reset_idf_schedules_path.init_eppy(arguments.get('idf_configuration'), **arguments)

	counter = 0

	base_folder = Path(arguments['oedi_download_folder'], arguments['bldg_download_folder_basename'])
	for scenario in os.listdir(base_folder):
		if ('.DS_Store' not in scenario) and ('.zip' not in scenario) and ('.csv' not in scenario): 
			print('\n')
			scenario_folder = Path(base_folder, scenario)

			for city in os.listdir(scenario_folder):
				if '.DS_Store' not in city: 
					print('\n')
					city_folder = Path(scenario_folder, city)

					for file in os.listdir(city_folder):
						if '.zip' in file: os.remove(Path(city_folder, file))
						elif '.DS_Store' not in file: 

							bldg_folder = Path(city_folder, file)
							upper_level_schedules = Path(bldg_folder, 'schedules.csv')

							for bldg_weather_year in os.listdir(bldg_folder):

								if ('.DS_Store' not in bldg_weather_year) and ('.csv' not in bldg_weather_year):
									bldg_weather_year_folder = Path(bldg_folder, bldg_weather_year)
									lower_level_schedules = Path(bldg_weather_year_folder, 'schedules.csv')

									if lower_level_schedules.exists():

										if not upper_level_schedules.exists():
											shutil.copy(lower_level_schedules, upper_level_schedules)

										os.remove(lower_level_schedules)


									for file in os.listdir(bldg_weather_year_folder):
										
										if '.idf' in file:

											idf_obj = reset_idf_schedules_path.init_eppy(Path(bldg_weather_year_folder, file), **arguments)
											
											# modify each schedule:File entry in an .idf
											for schedule in idf_obj.idfobjects['Schedule:File']:
												schedule.File_Name = str(upper_level_schedules)   # NOTE: Changed to use absolute file path 

											for field in configuration.idfobjects:

												# if the configuration file IDF object has instances of the field type (len > 0)                
												if len(configuration.idfobjects[field]) > 0:
													try: 
														idf_obj.idfobjects[field] = configuration.idfobjects[field]    # The building IDF may not have the field
													except:           
														# if the field isnt in the bldg file, add it then set its value 
														print(f'IDF does not have field {field}')
														# new_flag = idf_obj.newidfobject(field)
														idf_obj.idfobjects[field] = configuration.idfobjects[field]

											idf_obj.save()          # overwrite original with modifications

											counter = counter + 1
											elapsed_time = time.time() - startTime

											print(f'\r{scenario}. {city}. Completed {counter} idf updates. Rate: {round(counter/elapsed_time,1)}.', end="")

										if ('.xml' in file) and ('in.xml' not in file):
											
											ET.register_namespace("", "http://hpxmlonline.com/2019/10")
											ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
											ET.register_namespace("", 'http://hpxmlonline.com/2019/10') 

											file = Path(bldg_weather_year_folder, file)   
											
											try: 
												tree = ET.parse(file)
											except: 
												raise RuntimeError(f"Error loading bldg xml file {file}")

											root = tree.getroot()
																					
											xml_modifier.change_attrib_text(str(upper_level_schedules), root, attrib='SchedulesFilePath')
											
											# write the modified building xml file 
											tree.write(file, encoding="UTF-8", xml_declaration=True)