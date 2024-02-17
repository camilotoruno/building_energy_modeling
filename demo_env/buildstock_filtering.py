#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:06:21 2024

Filter a ResStock buildstock.csv (e.g. baseline_metadata_only.csv) by federal poverty level, 
city, and city size. 

@author: camilotoruno
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 
import random
from argparse import ArgumentParser
import os 

# def plotting_1():
#     total_income_bins = create_income_bins(obuildstock)
    
#     # check the income distribution differences between the subsample and original 
#     obuildstock2 = obuildstock
#     subset_income_bins = create_income_bins(obuildstock2)
#     diff = subset_income_bins.percentages - total_income_bins.percentages
#     # plt.bar(subset_income_bins.index, diff)
#     # plt.title('Percentage Income Shifts')
#     # plt.xticks(rotation=90)  # Rotate labels 90 degrees counterclockwise
#     # plt.show()
    
#     city_bins = obuildstock.value_counts('in.city')
    
#     # Create the histogram
#     plt.bar(subset_income_bins.index, subset_income_bins.values)
#     plt.xlabel("Low End of Annual Income")  # Replace with the label for the x-axis
#     plt.xticks(subset_income_bins.index, rotation=90)  # Rotate labels 90 degrees counterclockwise
#     plt.ylabel("Number of Houses Matching Criteria")
#     plt.title("Histogram of Houses Matching Criterion")
#     plt.show()


# def plotting_2(subset_income_bins):
#     # calculate the numebr of houses up to and including the income cutoff
#     per = []
#     no_houses = []
#     for income in subset_income_bins.index:
#         no_houses.append(sum(subset_income_bins[:income]))
#         per.append(sum(subset_income_bins[:income])/sum(subset_income_bins)*100)
    
#     fig, graph1 = plt.subplots()
    
#     graph1.bar(subset_income_bins.index, no_houses)
#     plt.xticks(subset_income_bins.index, rotation=90)  # Rotate labels 90 degrees counterclockwise
#     # plt.yticks(np.linspace(min(no_houses),max(no_houses), len(subset_income_bins)))
#     plt.yticks(no_houses)
    
#     graph2 = graph1.twinx()
#     graph2.bar(subset_income_bins.index, per)
#     plt.xlabel("Low End of Annual Income")  # Replace with the label for the x-axis
#     plt.ylabel("Per. Houses Up to and Including an Income Level")
#     plt.xticks(subset_income_bins.index, rotation=90)  # Rotate labels 90 degrees counterclockwise
#     # plt.yticks(np.linspace(min(per),max(per), len(subset_income_bins)))
#     plt.yticks(per)
#     plt.title("Houses with Income Equal & Above a Bin Value")
    
#     plt.grid()
#     plt.show()
    
#     # plt.bar(range(0, len(city_bins)), city_bins.values)
#     # plt.title('cities of 1-400 houses')
#     # plt.xticks(rotation=90)  # Rotate labels 90 degrees counterclockwise
#     # plt.show()
#     # print('sum of small cities, ', sum(city_bins.values))


def det_num_small_cities_can_sim(city_bins):
    sum_tot = 0
    city_bins = city_bins.sort_values()
    city_count = 2
    for i in range(0, len(city_bins)):
        if sum_tot + city_bins[i] < city_count*400:
            sum_tot = sum_tot + city_bins[i]
        else: break
    
    for j in range(0, i):
        print(city_bins.index[j])
    print(i, 'cities for price of ', city_count)
    
    print('\n\nRemember to re-ID the BUILDING ID!')
    

def filter_cities(buildstock, keep_cities, exclude_cities):
    # note this modifies the original buildstock object (?)
    
    print('\nfiltering cities')

    if exclude_cities != []:
        rows =  ~buildstock['in.city'].isin(exclude_cities)
        buildstock = buildstock[rows ]
        print('\tremoving ', sum(~rows), ' exclude cities houses')
        
    if keep_cities != []:
        rows = buildstock['in.city'].isin(keep_cities)
        print('\reamining ', sum(~rows), ' kept houses in cities houses')
        buildstock = buildstock[rows]   

    return buildstock


def filter_city_size(buildstock, city_size_limit, keep_cities):
    # for each city, limit the number of houses randomly 
    
    def count_remaining_houses(keep_cities):
        for city in keep_cities:
            print('\t', len( buildstock[ buildstock['in.city'] == city ] ), 'houses in', city)
    
    
    def generate_unique_list(city_size_limit, num_houses_in_city):
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
        if num_houses_in_city <= city_size_limit:
            unique_list = [i for i in range(num_houses_in_city)]
        
        else: 
            # Create a list of all possible values in the range
            all_values = list(range(num_houses_in_city))
        
            # Shuffle the list to randomize the order
            random.shuffle(all_values)
            
            # Select the desired number of unique values from the shuffled list
            unique_list = all_values[:city_size_limit]
        
        return unique_list
        
    
    print("Filtering by city size:", city_size_limit)
    count_remaining_houses(keep_cities)
    
    try: 
        # create a new table with the desired number of houses per city 
        rbuildstock = pd.DataFrame(columns = buildstock.columns)
        for city in keep_cities:
            city_buildstock = buildstock[ buildstock["in.city"] == city ]
            city_buildstock = city_buildstock.reset_index(drop=True)
            rows_2_keep = generate_unique_list(city_size_limit, len(city_buildstock))
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


def filter_poverty(buildstock, acceptable_federal_poverty_levels):
    print('filtering by poverty levels')
    buildstock = buildstock[ buildstock['in.federal_poverty_level'].isin(acceptable_federal_poverty_levels) ]
    print('\t', len(buildstock), 'house records remaining')
    return buildstock

def check_unique(buildstock):
    print('unique ratio', len(np.unique(buildstock.bldg_id.values))/len(buildstock))
    



def filtering(buildstock_folder, buildstock_file, federal_poverty_levels, 
              city_size_limit, keep_cities, exclude_cities, output_file, output_folder,
              save = False):   
    print('Loading data..')
    ibuildstock = pd.read_csv(os.path.join(buildstock_folder + buildstock_file))
    obuildstock = filter_cities(ibuildstock, keep_cities, exclude_cities)
    obuildstock = filter_poverty(obuildstock, federal_poverty_levels)
    obuildstock = obuildstock.reset_index(drop=True)   
    check_unique(obuildstock)
    obuildstock = filter_city_size(obuildstock, city_size_limit, keep_cities)
    check_unique(obuildstock)
    
    # reset the bldg index ids to ascending (maybe needed if metadata ran thru the ResStock/Openstudio workflows)
    # obuildstock['bldg_id'] = obuildstock.index.values + 1
    
    print('\nFinal:', len(obuildstock), 'house records remaining')
    if save:
        obuildstock.to_csv(os.path.join(output_folder, output_file), index=False)
        print('Filtered buildstock saved at', os.path.join(output_folder, output_file))
    else:
        print('Filtered buildstock not saved!')

if __name__ == "__main__":
    filtering()

#%% clean and filter buildstock



#%% Analyze the remaining housing stock 

# plotting_1()

#%%

# plotting_2()


#%% determine the number of small cities we could simulate for the price of a large city
# det_num_small_cities_can_sim(city_bins)


