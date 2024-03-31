#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 09:58:26 2024
@author: camilotoruno

TODO: 
    rename to BuildstockGenerateIDFs

"""
import xml.etree.ElementTree as ET
import os 
import subprocess
import json
import shutil
import functions.argument_builder as argument_builder
import multiprocessing
import math 
import tqdm 

class Job:
    def __init__(self, bldg, id, no_jobs, **arguments):
        self.bldg = bldg
        self.id = id
        self.no_jobs = no_jobs
        self.arguments = arguments
        

def run_job(job):

    # Build the openstudio arguments for this job and create a working copy of the base workflow folder
    openstudio_args = argument_builder.set_openstudio_args("workflow-" + str(job.id+1), **job.arguments)

    # if the working folder exists, delete it (it is only there for a given parallel run, files will be copied to output)
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
            print("\n\tError running OpenStudio:", result.stderr)
        if job.arguments["verbose"]:
            print("\n\tOpenStudio output:", result.stdout)
        
        # copy the generated .idf file to the correct output folder
        generated_idf = os.path.join(openstudio_args["openstudio_workflow_folder"], 'run', 'in.idf')
        shutil.copy(generated_idf, job.bldg.idf)
        
        # copy the run log
        shutil.copy(os.path.join(openstudio_args["openstudio_workflow_folder"], 'run', 'run.log'), 
                    os.path.join(job.bldg.folder, job.bldg.filebasename + "_osw.log"))

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
    
    Raises:
      ValueError: If the JSON file cannot be loaded or modified.
      subprocess.CalledProcessError: If the OpenStudio CLI command fails.
    """

    ET.register_namespace("", "http://hpxmlonline.com/2019/10")
    ET.register_namespace("xsi", 'http://www.w3.org/2001/XMLSchema-instance')
    ET.register_namespace("", 'http://hpxmlonline.com/2019/10')
    
    # Constrcut the jobs to be run in parallel 
    jobs = []
    for i, bldg in enumerate(buildings):
        idf_filename = os.path.join(bldg.folder, bldg.filebasename + ".idf")
        # if the overwite signal is true or the output doesn't exist 
        if kwargs.get('overwrite_output') or not(os.path.exists(idf_filename)):
            if kwargs.get('verbose') and os.path.exists(idf_filename): print(f'\tOutput file is being overwritten: {idf_filename}')

            jobs.append(Job(bldg, i, len(buildings), **kwargs))  # mark the building for processing
        elif kwargs.get('verbose') and os.path.exists(idf_filename) and not kwargs.get('overwrite_output'): 
            print(f'\tOutputfile exists and is not being overwritten: {idf_filename}')

    # Setup the job pool
    # at least one CPU core, up to max_cpu_load * num_cpu_cores, no more cores than jobs
    num_cpus = max(min( math.floor( kwargs.get('max_cpu_load') * multiprocessing.cpu_count()), len(jobs)), 1)    
    pool = multiprocessing.Pool(processes=num_cpus)
    no_jobs = len(jobs)
    
    # Execute the job pool and track progress with tqdm progress bar
    print(f'Generating {len(jobs)} .idf files using {num_cpus} CPU cores')
    for _ in tqdm.tqdm(pool.imap_unordered(run_job, jobs), total=no_jobs, desc="Generating .idf files", smoothing=0.01):
        pass

    # return the buildings that were operated on
    buildings = []
    for job in jobs: buildings.append(job.bldg)

    return buildings
    
    
    
    
    
    
    
