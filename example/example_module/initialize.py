import os
from uuid import uuid4
from pathlib import Path
from os.path import join,relpath

from rhodium_swmm.parameters import SwmmPathParameter
from rhodium_swmm.parameters import RhodiumParameter

from rhodium_swmm import swmm_problem
from rhodium_swmm.response import CostResponse, CoBenefitResponse, NodeRunoffVolumeResponse
from rhodium_swmm.model import RhodiumSwmmModel
from rhodium_swmm.lids import LidUsage
from rhodium.model import IntegerLever
from rhodium.model import CategoricalUncertainty
from rhodium import *
from .spatial_priorities import create_priority_dict
from rhodium_swmm.response import PriorityResponse
from rhodium_swmm.cli import cli
import pandas as pd
from rhodium_swmm import config
import pkgutil
import logging

def cli_entrypoint():
    config.RhodiumSwmmConfig.initialize = initialize_rhodium_swmm_model
    config.RhodiumSwmmConfig.parallel_initialize = parallel_initialize
    cli()

def parallel_initialize():
    env = str(uuid4())
    os.makedirs(env, exist_ok=True)
    os.chdir(env)
    return initialize_rhodium_swmm_model()

def get_data_files():
    package_path = os.path.dirname(__file__)
    data_path = join(package_path, "data")
    files = []
    for (dirpath, dirnames, filenames) in os.walk(data_path):
        tmp = [relpath(join(dirpath,f), package_path) for f in filenames]
        files.extend(tmp)

    return files

def initialize_files():
    files = get_data_files()

    for file_path in files:
        f = pkgutil.get_data(__name__,file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as writer:
            writer.write(f)

def initialize_rhodium_swmm_model(make_files=True):
    if(make_files):
        initialize_files()

    logging.basicConfig(filename = "platypus.log", level=logging.INFO)

    #----------------------------------------------------setting the cost parameters and uncertainties
    OM_cost_uncertainty = UniformUncertainty("OM_per_acre", 2382.89,4765.79)
    OM_cost = Parameter("OM_per_acre", default_value=2382.89)

    install_cost_uncertainty = UniformUncertainty("install_cost", 3623.9,4429.2 )
    install_cost = Parameter("install_cost", default_value=3623.9)


    lifetime_uncertainity= IntegerUncertainty("lifetime", 20,45)
    lifetime = Parameter("lifetime", default_value=25)

    cost_lid_type= pd.read_csv('data/cost_benefit/cost_lid_type.csv')

    #----------------------------------------------------setting the benefit parameters and uncertainties 
    park_benefit_uncertainty = UniformUncertainty("park_benefit", 915.76, 1660.87)
    park_benefit_acre = Parameter("park_benefit", default_value=1660.87)


    green_to_gray_uncertainty = UniformUncertainty("green_to_gray_benefit", 453.38, 591.87)
    green_to_gray = Parameter("green_to_gray_benefit", default_value=591.87 )


    GI_efficacy_uncertainty = UniformUncertainty("GI_efficacy", 0.5, 1)
    efficacy = Parameter("GI_efficacy", default_value=1)
    benefit_lid_type= pd.read_csv('data/cost_benefit/benefit_lid_type.csv')



    #assign random vacant percentages to each subcatchment 
    (aggregation_priority_dict, vacant_priority_dict, issue_priority_dict) = create_priority_dict()
    #vacant_priority_dict={'S1': 60, 'S2': 20, 'S3': 100, 'S4': 40, 'S5': 10, 'S6': 80, 'S7': 5 }

    #---------------------------------------------------setting the three responses/objectives
    responses = []
    responses.append(PriorityResponse("VacantPriority", vacant_priority_dict, dir=Response.MAXIMIZE))
    responses.append(CostResponse("Cost", cost_lid_type=cost_lid_type, install_cost=install_cost, lifetime=lifetime,  OM_per_acre=OM_cost, \
    parameters=[install_cost,OM_cost,lifetime], uncertainties=[install_cost_uncertainty,OM_cost_uncertainty,lifetime_uncertainity]))
    responses.append(NodeRunoffVolumeResponse("RunoffVolume", node_name=['O1']))
    
 
    
    #--------------------------------------------------read the swmm template and set the node name 
    rhodium_swmm_model = RhodiumSwmmModel(node_name="O1", swmm_input_file_template="data/swmm_data/swwm_input_template/Site_Drainage_Model.inp",   responses=responses)

    

    #--------------------------------------------------setting the levers 
    
    for subcatchment in rhodium_swmm_model.subcatchments:
     
        #set the maximum number of GI allowed to 100 or numbers to cover impervious area of the subcatchment, whichever is smaller 
        max_gi = min(100, rhodium_swmm_model.max_lids_per_subcatchment(subcatchment, 40))
        #print(subcatchment,":", max_gi)
        if max_gi > 0:
            
            lid = LidUsage(subcatchment, rhodium_swmm_model.lid_controls["LID_BRCell"], 1, 40, 4, 0, 100, 0, "*", "*", 0)
            lid.number = RhodiumParameter(IntegerLever(subcatchment+"_num_br", 0,max_gi), default=0)
            rhodium_swmm_model.lid_usages.append(lid)




    rhodium_swmm_model.update_rhodium_model()

    swmm_problem.set_model(rhodium_swmm_model)
    print("finished initializing")
    return rhodium_swmm_model