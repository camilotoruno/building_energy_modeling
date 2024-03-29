import os 
import glob
import copy 
import tqdm

def file_check(**kwargs):
    scenario_folders = kwargs.get('scenario_folders')        
    for i, city in enumerate(kwargs.get('keep_cities')):
        # Convert the building name from having spaces to having a dot for reading weather file format (e.g. Los Angles -> Los.Angeles)
        for scenario in scenario_folders:
            path = os.path.join( os.path.join(kwargs.get('weather_folder'), scenario, city.split(', ')[-1].replace(" ", ".")) )
            if not os.path.exists(path): raise IOError(f"Error Weather folder for {city} not found: {path}")

def weather_file_lookup(building_objects_list, **kwargs): 
    """ Find the weather files for each building and scenario and attach to each bldg in building objects list """
    print('Finding weather files for each city...')

    file_check(**kwargs)

    weather_folder = kwargs.get('weather_folder')
    verbose = kwargs.get('verbose')
    scenario_folders = kwargs.get('scenario_folders')        

    new_buildings = []      # create a longer list of buildings where each bldg object is associated with a single weather file

    # Convert the building name from having spaces to having a dot for reading weather file format (e.g. Los Angles -> Los.Angeles)
    weather_scenarios_for_city = [os.path.join(weather_folder, scenario, bldg.city.replace(" ", ".")) for scenario in scenario_folders]
    
    for bldg in tqdm.tqdm(building_objects_list, total=len(building_objects_list), desc='Finding EPW fines', smoothing=0.01):

        if verbose: print()

        for i, weather_scenario_4city in enumerate(weather_scenarios_for_city):          # for each weather scenario

            files = glob.glob(weather_scenario_4city + "/*.epw")
            if not files: raise FileNotFoundError(f"No weather located at {weather_scenario_4city!r}")
            
            # for each weather file in scenario 
            for filepath in files:                
                if ".epw" in filepath:

                    # Generate a whole bunch of folder structure / filenames
                    bldg.epw = filepath
                    bldg.epw_name = os.path.basename(bldg.epw).split('.epw')[0] 
                    bldg.weather_scenario = scenario_folders[i]#+ "-" + str(j) # add the scenario name 
                    bldg.filebasename = "bldg" + str(bldg.id) + "_" + bldg.epw_name
                    bldg_zip = "bldg" + bldg.id + "-up00.zip"  # add the prefix and suffix to filename
                    bldg.oedi_zip_fldr = os.path.join(kwargs.get('oedi_filepath'), bldg_zip)
                    bldg.zip = os.path.join(kwargs.get('oedi_download_folder'), kwargs.get('bldg_download_folder_basename'), bldg.weather_scenario, bldg.city, bldg_zip)
                    bldg.base_folder = os.path.join(kwargs.get('oedi_download_folder'), kwargs.get('bldg_download_folder_basename'), 
                                                    bldg.weather_scenario, bldg.city, bldg.zip.split('.zip')[0])

                    bldg.folder = os.path.join(bldg.base_folder, bldg.filebasename)
                    bldg.modified_xml = os.path.join(bldg.folder, bldg.filebasename + ".xml")
                    bldg.idf = os.path.join(bldg.folder, bldg.filebasename + ".idf")

                    new_buildings.append(copy.deepcopy(bldg))       # create a building file for each bldg and weather file pair 

                    if verbose: print('\tAdding', filepath, 'to building', bldg.id)
    
    if verbose: print()
    return new_buildings    # return bldg with weather file for each bldg for each weather file 