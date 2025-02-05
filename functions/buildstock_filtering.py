#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:06:21 2024

Filter a ResStock buildstock.csv (e.g. baseline_metadata_only.csv) by federal poverty level, 
city, and city size. 

@author: camilotoruno
"""

import pandas as pd 
import numpy as np 
import random
import os 
import math 


def filter_cities(buildstock, keep_cities, exclude_cities, verbose):
    # note this modifies the original buildstock object (?)
    
    if exclude_cities != []:
        rows =  ~buildstock['in.city'].isin(exclude_cities)
        buildstock = buildstock[rows ]
        if verbose: print('\tremoving ', sum(~rows), 'for exclude cities arg')
        
    if keep_cities != []:
        rows = buildstock['in.city'].isin(keep_cities)
        buildstock = buildstock[rows]   
        if verbose: print('\tremoving ', sum(~rows), 'for keep cities arg')

    return buildstock


def filter_city_size(buildstock, representative_sample_frac, keep_cities, verbose):
    # for each city, limit the number of houses randomly 
    
    def count_remaining_houses(keep_cities):
        for city in keep_cities:
            print('\tWorking with', len( buildstock[ buildstock['in.city'] == city ] ), 'houses in', city)
    
    
    def generate_unique_list(sample_size, num_houses_in_city):
        """
        Generates a list of the given length with unique integers from the specified range.
        
        Args:
          length: The desired length of the list.
          start: The starting value of the range (inclusive).
        
        Returns:
          A list of length 'length' containing unique integers from the range [0, num houses in city).
        
        Raises:
          ValueError: If the desired length is greater than the number of available unique values.
        """
        if num_houses_in_city <= sample_size:
            unique_list = [i for i in range(num_houses_in_city)]
        
        else: 
            # Create a list of all possible values in the range
            all_values = list(range(num_houses_in_city))
        
            # Shuffle the list to randomize the order
            # use the same seed so that if the same exact 
            # number of houses are required (from the same / for all cities )
            # the list is consistent. 
            random.seed(0)           
            random.shuffle(all_values)
            
            # Select the desired number of unique values from the shuffled list
            unique_list = all_values[:sample_size]
        
        return unique_list
        
    
    if verbose: 
        print("Taking statistically representative subsample")
        count_remaining_houses(keep_cities)
    
    try: 
        # create a new table with the desired number of houses per city 
        rbuildstock = pd.DataFrame(columns = buildstock.columns)
        for city in keep_cities:
            city_buildstock = buildstock[ buildstock["in.city"] == city ]
            city_buildstock = city_buildstock.reset_index(drop=True)
            tot_no_houses = len(city_buildstock)
            sample_size = math.ceil(tot_no_houses * representative_sample_frac[city]) # round up one house
            rows_2_keep = generate_unique_list(sample_size, len(city_buildstock))
            rbuildstock = pd.concat([rbuildstock, city_buildstock.iloc[ rows_2_keep ] ],
                                    axis= 0,
                                    ignore_index=True)                
        
        return rbuildstock
    
    except: 
        raise ValueError('Error building subsampled cities')


def create_income_bins(buildstock):  
    # count buildstock
    income_bins = buildstock.value_counts("in.income")  # Replace with the column to count
    income_bins = income_bins.sort_index()  # Sort in ascending order
    income_bins.index = income_bins.index.astype('str')
    income_bins.percentages = income_bins/sum(income_bins)*100
    return income_bins


def filter_poverty(buildstock, acceptable_federal_poverty_levels, verbose):
    if verbose: print('\tFiltering by poverty levels...')
    buildstock = buildstock[ buildstock['in.federal_poverty_level'].isin(acceptable_federal_poverty_levels) ]
    if verbose: print('\t', len(buildstock), 'house records remaining')
    return buildstock


def check_unique(buildstock):
    print('unique ratio', len(np.unique(buildstock.bldg_id.values))/len(buildstock))


def file_check(**kwargs):
    # check the input buildstock file exists
    if not os.path.exists(os.path.join(kwargs.get('buildstock_folder'), kwargs.get('buildstock_file'))):
        raise OSError(f"Could not find buildstock file {os.path.join(kwargs.get('buildstock_folder'), kwargs.get('buildstock_file'))}")
    if not os.path.exists(kwargs.get('buildstock_output_folder')):
        raise OSError(f"Could not find output folder {kwargs.get('buildstock_output_folder')}")


def determine_representative_sample_size(buildstock, keep_cities, statistical_sample_size, verbose):
    sub_samples = {}
    for city in keep_cities:
        if verbose: print(f"Determining representative sample size for {city}")
        total_num_houses = sum(buildstock["in.city"] == city)        
        sampling_fraction = min([statistical_sample_size / total_num_houses, 1])        # fraction cannot exceed 1 by use of min
        sub_samples.update({city: sampling_fraction})
            
    return sub_samples

def filtering(**kwargs): 
            
    buildstock_folder = kwargs.get('buildstock_folder') 
    buildstock_file = kwargs.get('buildstock_file') 
    federal_poverty_levels = kwargs.get('federal_poverty_levels') 
    keep_cities = kwargs.get('keep_cities') 
    exclude_cities = kwargs.get('exclude_cities') 
    output_folder = kwargs.get('buildstock_output_folder')
    statistical_sample_size = kwargs.get('statistical_sample_size')
    save_buildstock = kwargs.get('save_buildstock')
    verbose = kwargs.get('verbose')

    file_check(**kwargs)

    print('Loading buildstock and filtering..')
    ibuildstock = pd.read_csv(os.path.join(buildstock_folder, buildstock_file), low_memory=False)
    obuildstock = filter_cities(ibuildstock, keep_cities, exclude_cities, verbose)
    representative_sample_fracs = determine_representative_sample_size(obuildstock, keep_cities, statistical_sample_size, verbose)
    obuildstock = filter_poverty(obuildstock, federal_poverty_levels, verbose)
    obuildstock = obuildstock.reset_index(drop=True)   
    obuildstock = filter_city_size(obuildstock, representative_sample_fracs, keep_cities, verbose)
    
    print('\nBuildstock filtered.', len(obuildstock), 'houses remaining.')
    if save_buildstock:
        output_file = os.path.join(output_folder, kwargs.get('bldg_download_folder_basename'), 'buildstock.csv')
        obuildstock.to_csv(os.path.join(output_folder, output_file), index=False)
        if verbose: print('Filtered buildstock saved at', output_file)
    else:
        print('Filtered buildstock not saved!')