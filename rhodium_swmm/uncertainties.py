
from rhodium.model import CategoricalUncertainty
from rhodium_swmm.parameters import SwmmPathParameter
import pandas as pd 



class RainfallUncertainty(CategoricalUncertainty):

    def __init__(self, name,  rhodium_swmm_model, rainfall_categories_files_dict, default_category, previous_rainfall_file):
        #rainfall_categories_files_dict=create_rainfall_categories_files_dict()        
        super().__init__(name, rainfall_categories_files_dict.keys())
        #rainfall_parameter= SwmmPathParameter (self,rainfall_categories_files_dict, default=default_category)
        #rhodium_swmm_model.find_replace(["FILES", "RAINGAGES"], previous_rainfall_file, rainfall_parameter)



def create_rainfall_categories_files_dict(rainfall_categories_files_path="data/swmm_data/swmm_data_inputs/rainfall/rainfall_categories_files.csv"):

    rainfall_categories_files= pd.read_csv(rainfall_categories_files_path)
    rainfall_categories_files_dict = dict(zip(rainfall_categories_files.category, rainfall_categories_files.file))

    return rainfall_categories_files_dict



 
