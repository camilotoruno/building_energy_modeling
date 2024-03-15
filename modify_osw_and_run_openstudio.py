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
import shutil
import argument_builder
import multiprocessing
import time 


class Job:
    def __init__(self, bldg, id, no_jobs, **arguments):
        self.bldg = bldg
        self.id = id
        self.no_jobs = no_jobs
        self.arguments = arguments

       
def find_file_w_name_fragment(name_fragment, path):
    # return the first file with a given name_fragment in its file name
    for root, dirs, files in os.walk(path):
        for file in files:
            if name_fragment in file:
                return os.path.join(root, file)


def run_job(job):

    # Build the openstudio arguments for this job and create a working copy of the base workflow folder
    openstudio_args = argument_builder.set_openstudio_args("workflow-" + str(job.id+1), **job.arguments)

    # if the destination exists, delete it 
    if os.path.exists(openstudio_args["openstudio_workflow_folder"]):
        shutil.rmtree(openstudio_args["openstudio_workflow_folder"])

    shutil.copytree(openstudio_args['base_workflow'], openstudio_args["openstudio_workflow_folder"])

    if not os.path.exists(openstudio_args["osw_path"]):
        msg = f'Openstudio workflow {openstudio_args["osw_path"]} not found'
        raise FileNotFoundError(msg) 
    if not os.path.exists(openstudio_args["hpxml_measures_folder"]):
        raise FileNotFoundError(f'Openstudio directory {openstudio_args["hpxml_measures_folder"]} not found')
    
    try:
        # Load the JSON file
        with open(openstudio_args['osw_path'] , 'r') as f:
            openstudio_workflow_file = json.load(f)

        openstudio_workflow_file['steps'][0]['arguments']['hpxml_path'] = job.bldg.modified_xml  
        openstudio_workflow_file['steps'][0]['arguments']['output_dir'] = os.path.join('..', 'workflow', 'run')

        # Write the modified JSON back
        with open(openstudio_args['osw_path'], 'w') as f:
            json.dump(openstudio_workflow_file, f, indent=4)
    
        # call the openstudio command line interface
        result = subprocess.run(
            openstudio_args["cli_command"],
            shell = True,  # Set to False if not using shell features
            cwd = openstudio_args["hpxml_measures_folder"],
            capture_output = True,
            text = True
            )
        
        # Check for errors and process the output
        if result.returncode != 0:
            print("Error running OpenStudio:", result.stderr)
        if job.arguments["verbose"]:
            print("OpenStudio output:", result.stdout)
        
        # copy the generated .idf file to the correct output folder
        generated_idf = os.path.join(openstudio_args["openstudio_workflow_folder"], 'run', 'in.idf')
        output_idf = os.path.join(job.bldg.folder, job.bldg.filebasename + ".idf")
        shutil.copy(generated_idf, output_idf)
        
        # copy the generated schedules file to the correct output folder and save name to bldg object
        search_path = os.path.join(openstudio_args["openstudio_workflow_folder"], "generated_files")
        generated_schedule = find_file_w_name_fragment('schedule', search_path)  # find schedules file in openstudio output folder
        shutil.copy(generated_schedule, job.bldg.folder)
        job.bldg.schedules_new = os.path.basename(generated_schedule)

        # copy the run log
        shutil.copy(os.path.join(openstudio_args["openstudio_workflow_folder"], 'run', 'run.log'), 
                    os.path.join(job.bldg.folder, job.bldg.filebasename + "_osw.log"))
        job.bldg.new_schedule = os.path.join(job.bldg.folder, os.path.split(generated_schedule)[1])


    # raise errors if they occured while reading openstudio json file
    except (ValueError, json.JSONDecodeError) as e:
        raise Exception(f"Error modifying JSON for file {job.bldg.xml}: {e}")

    except subprocess.CalledProcessError as e:
        raise Exception(f"Error running OpenStudio CLI for file {job.bldg.xml}: {e}")

    # remove th working folder that was generated 
    shutil.rmtree(openstudio_args["openstudio_workflow_folder"])

    return job


def modify_and_run(buildings, **kwargs):
    
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
    startTime = time.time()

    ET.register_namespace("", "http://hpxmlonline.com/2019/10")
    ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
    ET.register_namespace("", 'http://hpxmlonline.com/2019/10')
    
    # Constrcut the jobs to be run in parallel 
    jobs = []
    for i, bldg in enumerate(buildings):
        jobs.append(Job(bldg, i, len(buildings), **kwargs))

    num_cpus = min(multiprocessing.cpu_count(), len(jobs)) - 2
    print(f'Generating {len(jobs)} .idf files using {num_cpus} CPU cores')
    pool = multiprocessing.Pool(processes=num_cpus)

    no_jobs = len(jobs)
    startTime = time.time()
    result = pool.map_async(run_job, jobs)
    while not result.ready():
        # Print remaining jobs (optional)
        no_completed = no_jobs - result._number_left
        if no_completed > 0:
            elapsed_time = time.time() - startTime
            rate = (no_completed / elapsed_time) * (60*60)        #hours
            est_remaining_time = round(no_jobs / rate, 2)
            print(f"Jobs remaining: {result._number_left}. Estimated time remaining {est_remaining_time} (hrs)")
            time.sleep(10)

    real_results = result.get()
    elapsed_time = round((time.time() - startTime) / 60/60, 2)
    print(f"{len(jobs)} jobs completed in {elapsed_time} seconds.")  # Print total completed jobs

    buildings = []
    for result in real_results:
        buildings.append(result.bldg)  # Assign results back to jobs

    return buildings
    
    
    
    
    
    
    
    
    
