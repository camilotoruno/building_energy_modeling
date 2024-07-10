import os 
import glob
import copy 
import tqdm
from pathlib import Path
import pandas as pd


def file_check(**kwargs):
    scenario_folders = kwargs.get('scenario_folders')        
    for i, city in enumerate(kwargs.get('keep_cities')):
        # Convert the building name from having spaces to having a dot for reading weather file format (e.g. Los Angles -> Los.Angeles)
        for scenario in scenario_folders:
            path = Path( kwargs.get('weather_folder'), scenario, city.split(', ')[-1].replace(" ", ".") ) 
            if not path.exists(): raise IOError(f"Error Weather folder for {city} not found: {path}")


def weather_file_lookup(building_objects_list, **kwargs): 
    """ Find the weather files for each building and scenario and attach to each bldg in building objects list """
    print('Finding weather files for each city...')

    file_check(**kwargs)

    weather_folder = kwargs.get('weather_folder')
    verbose = kwargs.get('verbose')
    scenario_folders = kwargs.get('scenario_folders')        
    new_buildings = []      # create a longer list of buildings where each bldg object is associated with a single weather file

    #TODO Find the files for each city, then assign them to each building in a city, rather than using each building to search for a city and all its files (reduce the number of searches signficantly)
    # make a list of cities 

    # make a list of all cities 
    cities = kwargs.get('keep_cities')
    cities = [city.split(', ')[1].replace(" ", ".") for city in cities]

    epw_files = []
    scenarios_list = []
    cities_list = []

    # for each city, make a list of weather files for that city 
    for j, city in enumerate(cities): 
        weather_scenarios_for_city = [os.path.join(weather_folder, scenario, city) for scenario in scenario_folders]  # make list of weather scenarios for city

        if verbose: print()

        for i, weather_scenario_4city in enumerate(weather_scenarios_for_city):          # for each weather scenario

            scenario = scenario_folders[i]

            files = glob.glob(weather_scenario_4city + "/*.epw")
            if not files: raise FileNotFoundError(f"No weather located at {weather_scenario_4city!r}")
            
            # for each weather file in scenario 
            for filepath in files:                
                if ".epw" in filepath:

                    scenarios_list.append(scenario)
                    cities_list.append(kwargs.get('keep_cities')[j].split(', ')[1])  # convert to just city name (drop state prefix)
                    epw_files.append(filepath)

    files_dataframe = pd.DataFrame({'City': cities_list, 'Scenario': scenarios_list, 'Weather Files': epw_files})

    # update the building objects list with the epw's we found for each city and scenario 
    for bldg in tqdm.tqdm(building_objects_list, total=len(building_objects_list), desc='Generating Building List from EPW files and BuildStock', smoothing=0.01):

        city_weather_files = files_dataframe[files_dataframe['City'] == bldg.city]

        if verbose: print()

        for index, row in city_weather_files.iterrows():          # for each weather file in the city-scenarios table 

            # Generate a whole bunch of folder structure / filenames
            bldg.epw = row['Weather Files']
            bldg.epw_name = os.path.basename(bldg.epw).split('.epw')[0] 
            bldg.weather_scenario = row['Scenario'] #+ "-" + str(j) # add the scenario name 
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