# building_energy_modeling

This repository provides a workflow script called script.py which coordinates the calls to functions that convert a ResStock buildstock.csv file to .idf files for EnergyPlus simulation. 

The script.py can be run from terminal or an IDE. Arguments for the functions are provided in an args dictionary. These define the input buildstock.csv file, local ResStock repository

## Package Setup:

To function this package requires that the ResStock repository resstock-euss.2022.1 (https://github.com/NREL/resstock/releases/tag/euss.2022.1) be downloaded. For the workflow to work the file ```custom-run-hpxml.osw``` must be located ```resstock-euss.2022.1/resources/hpxml-measures/workflow```. To meet these requirments simply unzip the copy of the ResStock repository held in this repository. This package also requires OpenStudio 3.4.0, the release and download versions for which can be found here (https://github.com/NREL/OpenStudio/releases?page=2). Note that OpenStudio released an update for the Windows installer after this release which may be necessary for some uses. 

Then you must add the OpenStudio package to the PATH environment variable. 
On Mac's Terminal enter ```export PATH=$PATH:~/usr/local/bin/openstudio```. 
        
For windows, follow these instructions to add to the PATH variable (https://learn.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14)). Based on my installation, the path to the openstudio.exe can be found at ```C:\openstudio-3.4.0\bin\openstudio.exe```, add this to the PATH variable. 

## Environment Setup
Create the required Python environment by calling ```conda create --name <env_name> python=3.11.4```

Then activate the environment using ```conda activate <env_name>```. Now install the required packages 

```pip install boto3==1.29.1 tqdm==4.65.0 pandas==2.1.4 argparse==1.4.0 eppy==0.5.63```

## Script.py Setup

To determine where your anaconda3 folder which contains the virtual environment you created: On windows from the ```Users/<user>``` folder in the command prompt enter ```dir /s anaconda3```. This will return something like ```C:\Users\ctoruno\AppData\Local```. Set the ```filtering_arguments``` dictionary entry ```"buildstock_folder"``` to the envrionment path (e.g. ```"\Users\ctoruno\AppData\Local\anaconda3\envs\<env_name>"```)

Describe the weather scenarios you want to run by listing the folders that contain weather. The assumed file structure is ```weather/<scenario>/<city>```. 

## Running workflow
    
Either run the script.py from your favorite IDE with the anaconda envrionment's python as the interpretter or Navigate to the folder where script.py is located. Activate your anaconda environment with ```conda activate <env_name>``` and then call ```python script.py```

