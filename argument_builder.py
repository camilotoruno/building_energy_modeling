import os

class argument_builder:

    def set_optional_args(arguments):
        # defaults for optional arguments
        if 'save_buildstock' not in arguments.keys(): arguments['save_buildstock'] = True
        if 'verbose' not in arguments.keys(): arguments["verbose"] = False
        if 'unzip' not in arguments.keys(): arguments['unzip'] = False
        return arguments

    def set_calculated_args(arguments):
        # set calculated/generated arguments 
        arguments['pathnameto_eppy'] = os.path.join(arguments['conda_venv_dir'], "lib", "python3.11", "site-packages", "eppy")
        arguments["iddfile"] = os.path.join(arguments["openstudio_application_path"], "EnergyPlus", "Energy+.idd")
        arguments["oedi_filepath"] = "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2022/resstock_amy2018_release_1/building_energy_models/upgrade=0/"
        return arguments

    def set_openstudio_args(cwd):
        # folder paths should not change 
        # set openstudio workflow for idf generation. Modified version of 
        # resstock-euss.2022.1/resources/hpxml-measures/workflow/template-run-hpxml.osw
        openstudio_workflow = "custom-run-hpxml.osw"
        hpxml_measures_folder = os.path.join(cwd, "resstock-euss.2022.1", "resources", "hpxml-measures")
        openstudio_workflow_folder = os.path.join(hpxml_measures_folder, "workflow")
        openstudio_workflow_file = os.path.join(openstudio_workflow_folder, openstudio_workflow)

        openstudio_args = {
            "openstudio_workflow": openstudio_workflow,
            "hpxml_measures_folder": hpxml_measures_folder,
            "openstudio_workflow_folder": openstudio_workflow_folder,
            "openstudio_working_dir": hpxml_measures_folder,
            "osw_path": openstudio_workflow_file
            }

        return openstudio_args