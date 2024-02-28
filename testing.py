#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 15:52:23 2024

@author: camilotoruno
"""

import multiprocessing

def square(num):
    return num * num

def processing():
    numbers = [1, 2, 3, 4, 5]
    num_processes = 2  # Use 2 processes
    
    # Create a pool of workers
    pool = multiprocessing.Pool(processes=num_processes)
    
    # Process numbers in parallel using map
    results = pool.map(square, numbers)
    
    # Close and join the pool
    pool.close()
    pool.join()
    
    # Print the results
    print(results)  # Output: [1, 4, 9, 16, 25]
    