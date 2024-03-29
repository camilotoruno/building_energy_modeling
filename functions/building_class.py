#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 20:32:22 2024

@author: camilotoruno
"""
import os 

class BuildingFilesData:
    """
    Represents a custom object with folder, schedule, and xml attributes.
    """
    def __init__(self, ID):
        # require initialization with the folder of the files for the building
        self.id = str(ID).zfill(7) # padd the building number with zeros
        self.city = None    
        self.weather_scenario = None
        self.filebasename = None

        ## Input files / folders
        self.folder = None
        self.xml = None        
        self.idf = None
        self.epw = None      
        self.epw_name = None

        ## Generated files 
        self.modified_xml = None     # list of modified xmls (one for each weather file)
        self.output_idf = None

        self.schedules = None
        self.schedules_new = None

        self.oedi_zip_fldr = None
        self.zip = None


    def assign_folders_contents(self):  
        for file in os.listdir(self.folder):
            filepath = os.path.join(self.folder, file)
            if "schedules.csv" in file and self.schedules == None:
                # original schedules file downloaded for OEDI 
                self.schedules = filepath
            elif "in.xml" in file and self.xml == None:
                self.xml = filepath
            elif "in.idf" in file and self.idf == None:
                self.idf = filepath 
            elif ('schedules' in file) and ("schedules.csv" not in file) and (self.schedules_new == None):
                # case for the genereated schedules file with a large
                # alpha numeric suffix that openstudio generates and 
                # points the .idf files to.  
                self.schedules_new = filepath
                

if __name__ == "__main__":
    # Code that executes only when the script is run directly
    # (This part is optional and can be left empty)
    None
