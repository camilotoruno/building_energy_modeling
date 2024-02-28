#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 09:58:26 2024

@author: camilotoruno
"""


import xml.etree.ElementTree as ET
import os 
import subprocess
import json
import xml_modifier 
import time
import shutil
from tqdm import tqdm
import multiprocessing
import concurrent.futures

class ProcessingJob:

    def __init__(self, bldg_obj):
        # require initialization with the folder of the files for the building
        self.bldg = bldg_obj

        
       
def find_file_w_name_fragment(name_fragment, path):
    # return the first file with a given name_fragment in its file name
    for root, dirs, files in os.walk(path):
        for file in files:
            if name_fragment in file:
                return os.path.join(root, file)

def generate_idf(job):
    
    # desired_directory = "/path/to/your/directory"
    os.chdir(job.openstudio_working_dir)
    
    # Set the environment variable to the new working directory
    os.environ["CWD"] = os.getcwd()

    try:
        # Load the JSON file
        with open(job.osw_path , 'r') as f:
            openstudio_workflow_file = json.load(f)
                
        openstudio_workflow_file['steps'][0]['arguments']['hpxml_path'] = job.bldg.modified_xml  
        openstudio_workflow_file['steps'][0]['arguments']['output_dir'] = job.osw_output_folder  

        # Write the modified JSON back
        with open(job.osw_path, 'w') as f:
            json.dump(openstudio_workflow_file, f, indent=4)
    
        # call the openstudio command line interface
        result = subprocess.run(
            job.cli_command,
            shell=True,  # Set to False if not using shell features
            cwd=job.openstudio_working_dir,
            capture_output=True,
            text=True
            )
        

        # # Check for errors and process the output
        # if result.returncode != 0:
        #     raise RuntimeError (f"Error running OpenStudio: {result.stdout}")
        
        # if 'Error' in result.stdout:
        #     raise RuntimeError (f"Error running OpenStudio: {result.stdout}")

        # copy the generated .idf file to the correct output folder
        generated_idf = os.path.join(job.run_folder, 'in.idf')
        shutil.copy(generated_idf, job.bldg.folder)
        
        # # REMOVE THIS AND JUST USE ORIGINAL SCHEDULES.CSV
        # # copy the generated schedules file to the correct output folder and save name to bldg object
        # search_path = os.path.join(openstudio_workflow_folder, "generated_files")
        # generated_schedule = find_file_w_name_fragment('schedule', search_path)  # find schedules file in openstudio output folder
        # shutil.copy(generated_schedule, building.folder)
    
    # # raise errors if they occured whle reading openstudio json file
    # except (ValueError, json.JSONDecodeError) as e:
    #     raise Exception(f"Error modifying JSON for file {job.bldg.xml}: {e}")

    # except subprocess.CalledProcessError as e:
    #     raise Exception(f"Error running OpenStudio CLI for file {job.bldg.xml}: {e}")
    
    except: None
    
    return result
    
def construc_job_list(building_folders_objects, **kwargs):
    
    # construct jobs for multiprocessing
    jobs = []
    for bldg in building_folders_objects:
        
        job = ProcessingJob(bldg)

        # construct the command line call to openstudio
        openstudio_path = kwargs.get('openstudio_path')

        if "workflow" in bldg.folder:
            folder_part = bldg.folder.split("hpxml-measures")[1].lstrip(os.sep)  # Remove leading separator if any
            job.workflow_rel_folder = os.path.join("", folder_part, kwargs.get('openstudio_workflow'))
        else: 
            raise IOError(f'workflow missing from building folder {bldg.folder}')
        job.openstudio_workflow = kwargs.get('openstudio_workflow').split('.osw')[0] + job.bldg.id + '.osw'
        job.cli_command = f"{openstudio_path} run --workflow workflow/{job.openstudio_workflow} --measures_only"

        job.openstudio_working_dir = kwargs.get("openstudio_working_dir")
        job.osw_path = os.path.join(os.path.split(kwargs.get("osw_path"))[0], job.openstudio_workflow)  # define the new filepath to the bldg's osw
        
        job.run_folder = os.path.join(kwargs.get('openstudio_workflow_folder'), 'run' + job.bldg.id)
        job.osw_output_folder = ".." + os.sep + os.path.join("", "workflow", 'run' + job.bldg.id) # manually construct path because openstudio requires ../ preceding path


        jobs.append(job)
        
        # generate the output folder for openstudio
        if os.path.exists(job.run_folder):
            shutil.rmtree(job.run_folder)
        os.mkdir(job.run_folder)
        
        shutil.copy(kwargs.get("osw_path"), job.osw_path)        # copy the openstudio workflow to the bldg folder
        shutil.copy("/Users/camilotoruno/resstock-euss.2022.1-2/resources/hpxml-measures/weather/G5100330.epw", 
                    os.path.join(job.run_folder, "in.idf"))
        

        # # Loop through the list and print attributes
        # print("Object attributes:")
        # for key, value in vars(job).items():
        #     print(f"  - {key}: {value}")
        # print()  # Print an empty line between objects
        
    return jobs 

def modify_and_run(building_folders_objects, **kwargs):
    
    """
    Iterates through filenames, modifies a JSON entry, and executes OpenStudio workflow.
    
    Args:
      filenames: A list of filenames.
      osw_path: The path to the JSON file to modify.
      cli_command: The OpenStudio CLI command string.
    
    Raises:
      ValueError: If the JSON file cannot be loaded or modified.
      subprocess.CalledProcessError: If the OpenStudio CLI command fails.
    """
    
    # load arguments 
    openstudio_working_dir = kwargs.get("openstudio_working_dir")
    osw_path = kwargs.get("osw_path")

    if not os.path.exists(osw_path):
        raise FileNotFoundError(f'Openstudio workflow {osw_path} not found') 
    if not os.path.exists(openstudio_working_dir):
        raise FileNotFoundError(f'Openstudio directory {openstudio_working_dir} not found')
    
    ET.register_namespace("", "http://hpxmlonline.com/2019/10")
    ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
    ET.register_namespace("", 'http://hpxmlonline.com/2019/10')
    
    jobs = construc_job_list(building_folders_objects, **kwargs)
    
    
    # Use tqdm to iterate with a progress bar
    # for job in tqdm(jobs, desc="Generating EnergyPlus files", smoothing=0.01): # smoothing near avg time est
    # for job in jobs:
    #     generate_idf(job)
    
    num_processes = 2  # Adjust as needed
    # with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
    #     results = executor.map(generate_idf, jobs)
    
    #     # Collect results as they become available
    #     for result in results:
    #         print(f"Command exited with code: {result}")  # Or process the results further
            
    # total_tasks = len(jobs)  # Assuming 'jobs' is a list containing your tasks

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        # Submit tasks and create a list of futures
        futures = [executor.submit(generate_idf, job) for job in jobs]

        # Create a progress bar with total number of tasks
        pbar = tqdm(total=len(jobs))
        results = []
        # Process results using as_completed
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append( future.result() )
                pbar.update()
                # print(f"Command exited with code: {result}")  # Or process the results further
            except Exception as e:
                pbar.write(f"Task failed with exception: {e}")
                pbar.update()  # Update progress even on failures

        # Close the progress bar
        pbar.close()
        
    print(f"Commands exited with code: {[res if 'Error' in res else None for res in [result.stdout for result in results]]}")  # Or process the results further

    # num_processes = multiprocessing.cpu_count()  # Use available CPU cores
    # pool = multiprocessing.Pool(processes=num_processes)

    # # Track completed tasks using a counter
    # completed_tasks = 0
    # total_tasks = len(jobs)

    # # Create a progress bar using tqdm
    # pbar = tqdm(total=total_tasks)

    # # Process tasks using map and update the progress bar
    # for _ in pool.imap(generate_idf, jobs):
    #     completed_tasks += 1
    #     pbar.update()

    # # Close the pool and stop the progress bar
    # pool.close()
    # pool.join()
    # pbar.close()
    
    
    # # update the bldg objects with new files 
    # for i in range(len(building_folders_objects)):
    #     building_folders_objects[i].assign_folders_contents()
        
    # return building_folders_objects
    
    
    
    
    
    
    
    
    