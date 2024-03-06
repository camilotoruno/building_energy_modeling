# building_energy_modeling

This repository provides a workflow script called script.py which coordinates the calls to functions that convert a ResStock buildstock.csv file to .idf files for EnergyPlus simulation. 

The script.py can be run from terminal or an IDE. Arguments for the functions are provided in an args dictionary. These define the input buildstock.csv file, local ResStock repository

To function this package requires that the ResStock repository resstock-euss.2022.1 (https://github.com/NREL/resstock/releases/tag/euss.2022.1) be downloaded. It also requires OpenStudio 3.4.0, the release and download versions for which can be found here (https://github.com/NREL/OpenStudio/releases?page=2). Note that OpenStudio released an update for the Windows installer on release after this which may be necessary for some uses. 

Create the required environment by calling conda env create --file conda_environment.yml
