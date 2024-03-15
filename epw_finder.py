import os 
import glob
import copy 

def weather_file_lookup(building_objects_list, **kwargs): 
    print('Looking up weather files for each city...')

               
    # Find the weather files for each building and scenario and attach to each bldg in building objects list

    weather_folder = kwargs.get('weather_folder')
    verbose = kwargs.get('verbose')
    scenario_folders = kwargs.get('scenario_folders')        

    new_buildings = []      # create a longer list of buildings where each bldg object is associated with a single weather file

    for i, bldg in enumerate(building_objects_list):
        weather_scenarios_for_city = [os.path.join(weather_folder, scenario, bldg.city) for scenario in scenario_folders]

        if verbose: 
            print()

        for i, weather_scenario_4city in enumerate(weather_scenarios_for_city):

            files = glob.glob(weather_scenario_4city + "/*.epw")

            if not files:
                msg = f"No weather located at {weather_scenario_4city!r}"
                raise FileNotFoundError(msg)
            
            for j, filepath in enumerate(os.listdir(weather_scenario_4city)):
                
                if ".epw" in filepath:
                    bldg.epw = filepath
                    bldg.weather_scenario = scenario_folders[i] + "-" + str(j) # add the scenario name 
                    bldg.filebasename = "bldg" + bldg.id + "_" + bldg.weather_scenario
                    new_buildings.append(copy.deepcopy(bldg))

                    if verbose: 
                        print('\tAdding', filepath, 'to building', bldg.id)
                    
    return new_buildings