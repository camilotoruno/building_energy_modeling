import os 
import glob
import copy 

def weather_file_lookup(building_objects_list, **kwargs): 
    print('Finding weather files for each city...')

    # Find the weather files for each building and scenario and attach to each bldg in building objects list

    weather_folder = kwargs.get('weather_folder')
    verbose = kwargs.get('verbose')
    scenario_folders = kwargs.get('scenario_folders')        

    new_buildings = []      # create a longer list of buildings where each bldg object is associated with a single weather file

    for i, bldg in enumerate(building_objects_list):
        # Convert the building name from having spaces to having a dot for reading weather file format
        weather_scenarios_for_city = [os.path.join(weather_folder, scenario, bldg.city.replace(" ", ".")) for scenario in scenario_folders]

        if verbose: print()

        # for each weather scenario
        for i, weather_scenario_4city in enumerate(weather_scenarios_for_city):

            files = glob.glob(weather_scenario_4city + "/*.epw")

            if not files:
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