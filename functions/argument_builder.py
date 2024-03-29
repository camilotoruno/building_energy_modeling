import os
from sys import platform 

# import custom classes and functions
from functions import oedi_querying 
from functions import buildstock_filtering 
from functions import epw_finder

def file_check(**arguments):
    

    # Check for file locations before performing workflow. 
    buildstock_filtering.file_check(**arguments)
    oedi_querying.file_check(None, **arguments)
    epw_finder.file_check(**arguments)

    # # If no errors occured then it prints
    # print('Output files overwritten:', arguments[''])
    # print("Relative folder paths for input and output files generated. Required input folders present and outputfolders overwritten ({arguments}).")


def set_optional_args(arguments):
    # defaults for optional arguments
    if 'save_buildstock' not in arguments.keys(): arguments['save_buildstock'] = True
    if 'verbose' not in arguments.keys(): arguments["verbose"] = False
    if 'unzip' not in arguments.keys(): arguments['unzip'] = False
    return arguments


def set_calculated_args(arguments):
    # set calculated/generated arguments 
    if platform == 'darwin':  # mac system
        arguments['pathnameto_eppy'] = os.path.join(arguments['conda_venv_dir'], "lib", "python3.11", "site-packages", "eppy")
    elif platform == 'win32':  # windows
        arguments['pathnameto_eppy'] = os.path.join(arguments['conda_venv_dir'], "Lib", "site-packages", "eppy")
    else:
        raise OSError('Operating System not recognized.')

    arguments["iddfile"] = os.path.join(arguments["openstudio_application_path"], "EnergyPlus", "Energy+.idd")
    arguments["oedi_filepath"] = "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/building_energy_models/upgrade=0/"
    return arguments


def set_openstudio_args(workflow_copy, **kwargs):
    # folder paths should not change 
    # set openstudio workflow for idf generation. Modified version of 
    # resstock-euss.2022.1/resources/hpxml-measures/workflow/template-run-hpxml.osw
    cwd = kwargs.get('cwd')
    openstudio_path = kwargs.get('openstudio_path')
    hpxml_measures_folder = os.path.join(cwd, "resstock-euss.2022.1", "resources", "hpxml-measures")
    openstudio_workflow_folder = os.path.join(hpxml_measures_folder, workflow_copy)
    openstudio_workflow = "custom-run-hpxml.osw"
    openstudio_workflow_file = os.path.join(openstudio_workflow_folder, openstudio_workflow)
    base_workflow = os.path.join(cwd, "resstock-euss.2022.1", "resources", "hpxml-measures", "workflow")

    # construct the command line call to openstudio
    cli_command = f"{openstudio_path} run --workflow {workflow_copy}/{openstudio_workflow} --measures_only"


    openstudio_args = {
        "openstudio_workflow": openstudio_workflow,
        "hpxml_measures_folder": hpxml_measures_folder,
        "openstudio_workflow_folder": openstudio_workflow_folder,
        "osw_path": openstudio_workflow_file,
        "base_workflow": base_workflow,
        "cli_command": cli_command
        }

    return openstudio_args