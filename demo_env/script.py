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
import time
from reset_idf_schedules_path import Set_Relative_Schedules_Filepath

overwrite_download_folders = True

hpxml_measures_folder = "/Users/camilotoruno/resstock-euss.2022.1/resources/hpxml-measures"
osw_path = "/Users/camilotoruno/resstock-euss.2022.1/resources/hpxml-measures/workflow/custom-run-hpxml.osw"
buildstock_file = "baseline_metadata_only.csv"
# buildstock_file = "baseline_metadata_only_example_subset.csv"

buildstock_folder = "/Users/camilotoruno/anaconda3/envs/research/research_data/"
buildstock_output_file = "testing.csv"
output_buildstock_folder = hpxml_measures_folder
federal_poverty_levels = ['0-100%', '100-150%', '150-200%']
city_size_limit = 2
# keep_cities = [
#                 "AZ, Phoenix",
#                 "CA, Los Angeles",
#                 "CO, Denver",
#                 "FL, Orlando",
#                 "GA, Atlanta",
#                 "ID, Boise City",
#                 "IL, Chicago",
#                 "KS, Kansas City",
#                 "MA, Boston",
#                 "MI, Detroit",
#                 "MN, Minneapolis",
#                 "NE, Omaha",
#                 "NY, New York",
#                 "PA, Philadelphia",
#                 "TX, Dallas"
#                 ]

keep_cities = [
                "MI, Detroit",
                "TX, Dallas"
                ]
exclude_cities = ['In another census Place', 'Not in a census Place']

unzipped_folders_folder = "test_unzipped_building_energy_models"
zipped_folders_folder = "test_zipped_building_energy_models"
oedi_download_folder = "/Users/camilotoruno/resstock-euss.2022.1/resources/hpxml-measures/workflow"

#%%

buildstock_filtering.filtering(buildstock_folder = buildstock_folder,
                            buildstock_file=  buildstock_file,
                            federal_poverty_levels= federal_poverty_levels,
                            city_size_limit = city_size_limit,
                            keep_cities = keep_cities,
                            exclude_cities =  exclude_cities,
                            output_folder = output_buildstock_folder,
                            output_file = buildstock_output_file,
                            save = True,
                            verbose = False)


startTime = time.time()         # for timing the long portion of the script

print('\n')
oedi_querying.download_unzip(buildstock_file = buildstock_output_file,
                            buildstock_folder = output_buildstock_folder,
                            oedi_filepath="nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/building_energy_models/upgrade=0/", 
                            download_folder = oedi_download_folder, 
                            zip_folder= zipped_folders_folder, 
                            unzip_folder= unzipped_folders_folder,
                            overwrite= overwrite_download_folders,
                            unzip=True)


# modify the .xml files to remove uncessary info 
xml_modifier.modify_xml_files(oedi_download_folder, unzipped_folders_folder)


# call the openstudi command line interface to generate the .idf from .xml 
openstudio_path = "/usr/local/bin/openstudio"  
cli_command = f"{openstudio_path} run --workflow workflow/custom-run-hpxml.osw --measures_only"
modify_osw_and_run_openstudio.modify_and_run(oedi_download_folder = oedi_download_folder,
                                    unzip_folder = unzipped_folders_folder,
                                    osw_path = osw_path,
                                    openstudio_working_dir = hpxml_measures_folder,
                                    cli_command = cli_command,
                                    verbose=False)

print('Querying and running OpenStudio workflow time (min):', round((time.time()-startTime)/60, 1))


# Reset the .idf files' schedules file path to be relative (assumes schedules in same folder as idf)
iddfile = "/Applications/OpenStudio-3.4.0/EnergyPlus/Energy+.idd"
pathnameto_eppy = "/Users/camilotoruno/anaconda3/envs/research/lib/python3.11/site-packages/eppy"
Set_Relative_Schedules_Filepath(iddfile = iddfile,
                                pathnameto_eppy = pathnameto_eppy, 
                                unzipped_buildings_folder = unzipped_folders_folder,
                                openstudio_workflow_dir = oedi_download_folder
                                )

print('Workflow completed')
    
    
    
    
    
    
    
    