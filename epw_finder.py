import os 
import glob
import copy 


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

    for i, bldg in enumerate(building_objects_list):
        # Convert the building name from having spaces to having a dot for reading weather file format (e.g. Los Angles -> Los.Angeles)
        weather_scenarios_for_city = [os.path.join(weather_folder, scenario, bldg.city.replace(" ", ".")) for scenario in scenario_folders]

        if verbose: print()

        # for each weather scenario
        for i, weather_scenario_4city in enumerate(weather_scenarios_for_city):

            files = glob.glob(weather_scenario_4city + "/*.epw")

            if not files:
                print("files:", files)
                msg = f"No weather located at {weather_scenario_4city!r}"
                raise FileNotFoundError(msg)
            
            # for each weather file in scenario 
            for j, filepath in enumerate(files):                
                if ".epw" in filepath:
                    bldg.epw = filepath
                    bldg.weather_scenario = scenario_folders[i] + "-" + str(j) # add the scenario name 
                    bldg.filebasename = "bldg" + bldg.id + "_" + bldg.weather_scenario
                    new_buildings.append(copy.deepcopy(bldg))       # create a building file for each bldg and weather file pair 

                    if verbose: print('\tAdding', filepath, 'to building', bldg.id)
    
    if verbose: print()
    return new_buildings    # return bldg with weather file for each bldg for each weather file 