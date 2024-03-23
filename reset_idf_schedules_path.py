#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 23:53:49 2024

@author: camilotoruno
"""

from eppy.modeleditor import IDF
from tqdm import tqdm
import sys
import os 

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


def Set_Relative_Schedules_Filepath(buildings, **kwargs):

    for bldg in buildings:
        # remove all of schedule path besides filename. Requires that all downstream 
        # proceessing has idf and schedules in the same folder for a given building 
    
        idf_obj = init_eppy(bldg.output_idf, **kwargs)
        
        # modify each schedule:File entry in an .idf
        for schedule in idf_obj.idfobjects['Schedule:File']:
            # remove all the filepath, leaving just the file name for relative file path
            # instead of absolute file path
            schedule.File_Name = schedule.File_Name.split('/')[-1]
            
        # overwrite original with modifications
        idf_obj.save()


def Set_EnergyPlus_Simulation_Output(buildings, **kwargs):
    print('Set_EnergyPlus_Simulation_Output')

    for

    idf_obj = init_eppy(idf, **kwargs)

    # Define the desired output file settings
    # idf_obj.idfobjects['OutputControl:Files']

    # print(idf_obj.idfobjects['OutputControl:Files'])

    file_output_options = {
        'Output_MTR': 'Yes',                       
        'Output_ESO': 'Yes',                       
        'Output_Tabular': 'No',                      
        'Output_SQLite': 'No',                      
        'Output_JSON': 'No',     
    }


    output_Control_files = idf_obj.idfobjects['OutputControl:Files'][0]
    # print(output_Control_files)
    # print(type(output_Control_files))
    # print(dir(output_Control_files))

    for attrib, value in file_output_options.items():
        if not hasattr(output_Control_files, attrib): raise RuntimeError(f'IDF file does not have output options attribute {attrib}')        
        setattr(output_Control_files, attrib, value)         
    
    # print(output_Control_files)

    # Define the desired meter entries
    meter_entries = [
        ("NaturalGas:Facility", "Daily"),
        ("Electricity:Facility", "Timestep"),
        ("Electricity:Facility", "Daily"),
        ("Electricity:Facility", "Timestep"),
        ("NaturalGas:Facility", "Timestep"),
        ("DistrictCooling:Facility", "Timestep"),
        ("DistrictHeatingWater:Facility", "Timestep"),
    ]

    new_output_variables = [
    # Output:Variable
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
    
    for new_output_var in new_output_variables:
        new_flag = idf_obj.newidfobject('Output:Variable')  # generate a new IDF output variable object
        for value, attrib in new_output_var.items():        # for each of the value and attributes of the output variable
            setattr(new_flag, attrib, value)                # set the idf attribute to the desired value
    for output_var in idf_obj.idfobjects['Output:Variable']: print(output_var)


    new_Output_Meters = [
    # Output:Meter,
        {"Electricity:Facility": "Key_Name",
        "Timestep": "Reporting_Frequency"},

        {"NaturalGas:Facility": "Key_Name",
        "Timestep": "Reporting_Frequency"},

        {"DistrictCooling:Facility": "Key_Name",
        "Timestep": "Reporting_Frequency"},

        {"DistrictHeatingWater:Facility:": "Key_Name",
        "Timestep": "Reporting_Frequency"}
    ]

    # new_flag = idf_obj.newidfobject('Output:Meter')  # generate a new IDF output variable object
    for new_output_meter in new_Output_Meters:
        new_flag = idf_obj.newidfobject('Output:Meter')  # generate a new IDF output variable object
        for value, attrib in new_output_meter.items():        # for each of the value and attributes of the output variable
            setattr(new_flag, attrib, value)                # set the idf attribute to the desired value
    for output_var in idf_obj.idfobjects['Output:Meter']: print(output_var)


    new_Outputs_MeterFileOnly = [
    # Output:Meter:MeterFileOnly,
        {"NaturalGas:Facility": "Key_Name",
        "Daily": "Reporting_Frequency"},

        {"Electricity:Facility": "Key_Name",
        "Timestep": "Reporting_Frequency"},

        {"Electricity:Facility": "Key_Name",
        "Daily": "Reporting_Frequency"}
    ]

    for new_Output_MeterFileOnly in new_Outputs_MeterFileOnly:
        new_flag = idf_obj.newidfobject('Output:Meter:MeterFileOnly')  # generate a new IDF output variable object
        for value, attrib in new_Output_MeterFileOnly.items():        # for each of the value and attributes of the output variable
            setattr(new_flag, attrib, value)                # set the idf attribute to the desired value
    for output_var in idf_obj.idfobjects['Output:Meter:MeterFileOnly']: print(output_var)

    # overwrite original with modifications
    idf_obj.save()