# building_energy_modeling

This repository provides a workflow script called script.py which coordinates the calls to functions that convert a ResStock buildstock.csv file to .idf files for EnergyPlus simulation. 

The script.py can be run from terminal or an IDE. Arguments for the functions are provided in an args dictionary. These define the input buildstock.csv file, local ResStock repository

To function this package requires that the ResStock repository resstock-euss.2022.1 (https://github.com/NREL/resstock/releases/tag/euss.2022.1) be downloaded. 

Create the required environment by calling conda env create --file conda_environment.yml
