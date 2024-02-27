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
# import file_tree_cleanup 
import os


#%%

            
"""
INITITALIZE BUILDINGS OBJECT LIST IN THE BUILDSTOCK FILTERING AND 
DETERMINE WHICH CITY AND ID NUMBER EACH ONE IS. PASS THAT DATA TO THE NEXT 
FUNCTION THAT NEEDS THE BLDG OBJECT INFO 
"""
hpxml_measures_folder = "/Users/camilotoruno/resstock-euss.2022.1/resources/hpxml-measures"
openstudio_workflow_folder = os.path.join(hpxml_measures_folder, "workflow")
openstudio_workflow = "custom-run-hpxml.osw"
openstudio_workflow_file = os.path.join(openstudio_workflow_folder, openstudio_workflow)

args = {
        "hpxml_measures_folder": hpxml_measures_folder,
        "output_buildstock_folder": hpxml_measures_folder,
        "osw_path": openstudio_workflow_file,
        "buildstock_file": "baseline_metadata_only.csv",
        # "buildstock_file": "baseline_metadata_only_example_subset.csv",
        "buildstock_folder": "/Users/camilotoruno/anaconda3/envs/research/research_data/",
        "buildstock_output_file": "testing.csv",
        "buildstock_output_folder": hpxml_measures_folder,

        "federal_poverty_levels": ['0-100%', '100-150%', '150-200%'],
        "city_size_limit": 2,
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
        
        "openstudio_workflow": openstudio_workflow,
        "openstudio_path": "/usr/local/bin/openstudio",
        "openstudio_workflow_folder": openstudio_workflow_folder,
        "openstudio_working_dir": hpxml_measures_folder,
        
        "iddfile": "/Applications/OpenStudio-3.4.0/EnergyPlus/Energy+.idd",
        "pathnameto_eppy": "/Users/camilotoruno/anaconda3/envs/research/lib/python3.11/site-packages/eppy",
            
        'verbose': False, 
        "unzip": True,
        'overwrite_download_folders': True,
        'save': True
        }

# filter the buildstock data by the desired characteristics 
building_objects_list = buildstock_filtering.filtering(**args)

# query oedi for the required building zip file
print('\n')
startTime = time.time()         # for timing the long portion of the script
building_objects_list = oedi_querying.download_unzip(building_objects_list, **args)

#  modify the xml files to allow openstudio workflow to run 
building_objects_list = xml_modifier.modify_xml_files(building_objects_list)

# call the openstudi command line interface to generate the .idf from .xml 
building_objects_list = modify_osw_and_run_openstudio.modify_and_run(building_objects_list, **args)
print('Querying and running OpenStudio workflow time (min):', round((time.time()-startTime)/60, 1))

# Reset the .idf files' schedules file path to be relative (assumes schedules in same folder as idf)
Set_Relative_Schedules_Filepath(building_objects_list, **args)
print('Workflow completed')
    
    
    
    
    
    
    
    