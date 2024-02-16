#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 23:02:00 2024

@author: camilotoruno
"""

import oedi_querying 

buildstock_file = "/Users/camilotoruno/anaconda3/envs/research/research_data/city-fpl_filtered_baseline_metadata_only_example_subset.csv"

oedi_querying.download_unzip(buildstock_file=buildstock_file,
                    oedi_filepath="nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/building_energy_models/upgrade=0/", 
                    download_folder="/Users/camilotoruno/anaconda3/envs/research/research_data/", 
                    zip_folder="test_zipped_building_energy_models/", 
                    unzip_folder="test_building_energy_models/",
                    overwrite=True,
                    unzip=True)

# from multiprocessing import Process
 
# def func1(counter: int):
#     print("start func 1")
#     for i in range(100):
#         counter += 1
#         print("func 1", counter)
#     print("end func 1")
 
# def func2(counter: int):
#     print("start func 2")
#     for i in range(100):
#         counter += 1
#         print("func 2", counter)
#     print("end func 2")
    
# if __name__ == "__main__":
#     counter1 = 0
#     counter2 = 0
#     p1 = Process(target = func1, args=(counter1,))
#     # p2 = Process(target = func2, args=(counter2,))
#     p1.start()
#     # p2.start()
#     p1.join()
#     # p2.join()

# def fp(name, numList=None, what='no'):
#     print ('hello %s %s' % (name, what))
#     numList.append(name+'44')

# if __name__ == '__main__':

#     manager = Manager()

#     numList = manager.list()
#     for i in range(10):
#         keywords = {'what': 'yes', 'numList': numList}
#         p = Process(target=fp, args=['bob'+str(i)], kwargs=keywords)
#         p.start()
#         print("Start done")
#         p.join()
#         print("Join done")
#     print (numList)
    
    
    
    
    
    
    
    
    