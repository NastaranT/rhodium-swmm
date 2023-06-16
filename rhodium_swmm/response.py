from rhodium.model import Lever, Parameter, Response, Uncertainty
from .swmm.run import swmm_run_from_dict
import math
import pandas as pd



class RhodiumSwmmResponse(Response):

    def __init__(self, name, dir=Response.INFO, uncertainties=[], levers=[], parameters=[], **kwargs):
        super().__init__(name, dir=dir, **kwargs)

        self.uncertainties=uncertainties
        self.levers=levers
        self.parameters=parameters

    def calculate(self, swmm_model, binary_output, **kwargs):
        raise NotImplementedError



class PriorityResponse(RhodiumSwmmResponse):

    def __init__(self, name, priority_dict, dir=Response.MAXIMIZE, **kwargs):
        self.priority_dict = priority_dict
        super().__init__(name, dir=dir, **kwargs)

    def calculate(self, swmm_model, binary_output, **kwargs):
        priority_score = 0
        total_area = 0
        skipped = 0
        for lid in swmm_model.lid_usages:
            priority = self.priority_dict.get(lid.subcatchment)
            if priority is None:
                skipped += 1
                continue
            area = lid.area * lid.number
            total_area += area

            priority_score += area * priority

        print("Skipped: ", skipped)

        if total_area==0:
            priority_score=0
        else:
            priority_score = priority_score / total_area

        return priority_score 


class NodeRunoffVolumeResponse(RhodiumSwmmResponse):

    def __init__(self, name, node_name, dir=Response.MINIMIZE, **kwargs):

        self.node_name=node_name
       
        super().__init__(name, dir=dir, **kwargs)

    def calculate(self, swmm_model, binary_output, **kwargs):
        return binary_output["peak_flowrate"]
        #return binary_output["average_flowrate"]
        #return binary_output["peak_total_inflow"]

class SubcatRunoffVolumeResponse(RhodiumSwmmResponse):

    def __init__(self, name, subcat_name, dir=Response.MINIMIZE, **kwargs):

        self.subcat_name=subcat_name
       
        super().__init__(name, dir=dir, **kwargs)

    def calculate(self, swmm_model, binary_output, **kwargs):
        #return binary_output["runoff"]
        return binary_output

class CostResponse(RhodiumSwmmResponse):

    def __init__(self, name, cost_lid_type, install_cost=None, lifetime=None, per_tree_cost=None,  OM_per_acre=None, dir=Response.MINIMIZE, **kwargs):
        
        self.cost_lid_type= cost_lid_type
        self.install_cost=install_cost
        self.lifetime=lifetime
        self.per_tree_cost= per_tree_cost
        self.OM_per_acre = OM_per_acre

        super().__init__(name, dir=dir, **kwargs)

    
    def calculate_cost(self, lid_number, lid_area, discount_rate, plan_horizon, installation_year,install_cost, lifetime, OM_per_acre, **kwargs):

        
        area_acre = lid_area/43560
        cost = [None] * plan_horizon
        
        #number_trees = (lid_number * lid_area)/50          
        print("lifetime check: -------",lifetime)
        for year in range(len(cost)):

            if year < installation_year:
                cost[year] = 0
            elif year == installation_year or year == lifetime:
                cost[year] = ((lid_number* install_cost) + (lid_number * area_acre * OM_per_acre)) / (math.exp(discount_rate*(year+1)))
            else:
                cost[year] = (lid_number * area_acre * OM_per_acre)  / (math.exp(discount_rate*(year+1)))
               
    
        cost_discounted = sum(cost)
        return cost_discounted
    

    
    def calculate(self, swmm_model, binary_output, **kwargs):

        discount_rate = 0.0275
        plan_horizon = 40
        lid_usages= swmm_model.lid_usages
        total_discounted_cost = 0


        for lid in lid_usages:
        
                installation_year= list(self.cost_lid_type.loc[self.cost_lid_type['lid_type'] == lid.lid_process.lid_type, 'installation_year'])[0]
                if self.install_cost is None:
                    install_cost= list(self.cost_lid_type.loc[self.cost_lid_type['lid_type'] == lid.lid_process.lid_type, 'install_cost'])[0]
                else:
                    install_cost=kwargs[self.install_cost.name]
                
                if self.lifetime is None:
                    lifetime= list(self.cost_lid_type.loc[self.cost_lid_type['lid_type'] == lid.lid_process.lid_type, 'lifetime'])[0]
                else:
                    lifetime=kwargs[self.lifetime.name]
                
                # if self.per_tree_cost is None:
                #     per_tree_cost= list(self.cost_lid_type.loc[self.cost_lid_type['lid_type'] == lid.lid_process.lid_type, 'per_tree_cost'])[0]
                # else:
                #     per_tree_cost=kwargs[self.per_tree_cost.name]
                
                if self.OM_per_acre is None:
                    OM_per_acre= list(self.cost_lid_type.loc[self.cost_lid_type['lid_type'] == lid.lid_process.lid_type, 'OM_per_acre'])[0]
                else:
                    OM_per_acre=kwargs[self.OM_per_acre.name]
                total_discounted_cost = total_discounted_cost + self.calculate_cost(lid.number, lid.area, discount_rate, plan_horizon, installation_year, install_cost, lifetime, OM_per_acre)

            
        return total_discounted_cost



class CoBenefitResponse(RhodiumSwmmResponse):

    def __init__(self, name,benefit_lid_type, green_to_gray_benefit=None, park_benefit=None, GI_efficacy=None, dir=Response.MAXIMIZE, **kwargs):

        self.benefit_lid_type= benefit_lid_type
        #self.per_tree_benefit=per_tree_benefit
        self.green_to_gray_benefit= green_to_gray_benefit
        self.park_benefit=park_benefit
        self.GI_efficacy= GI_efficacy

        super().__init__(name, dir=dir, **kwargs)


    def calculate_cobenefits(self, lid_number, lid_area, discount_rate, plan_horizon, green_to_gray_benefit, park_benefit, GI_efficacy, **kwargs):


        area_acre = lid_area/43560
        #number_trees = (lid_number *lid_area)/50
        benefit = [None] * plan_horizon

        for year in range(len(benefit)):

            if lid_number*area_acre > 0.07:
                benefit[year] = ((lid_number * area_acre * park_benefit) * GI_efficacy)/ (math.exp(discount_rate*(year+1)))

            else:
                benefit[year] = ((lid_number * area_acre * green_to_gray_benefit)* GI_efficacy)/ (math.exp(discount_rate*(year+1)))
                #/(math.exp(discount_rate*(year+1)))

        benefit_discounted = sum(benefit)
        return benefit_discounted

    def calculate(self, swmm_model, binary_output, **kwargs):


        discount_rate = 0.0275
        plan_horizon = 40
        lid_usages= swmm_model.lid_usages
        total_discounted_cobenefits = 0
       

        for lid in lid_usages:
        
                installation_year= list(self.benefit_lid_type.loc[self.benefit_lid_type['lid_type'] == lid.lid_process.lid_type, 'installation_year'])[0]
                if self.green_to_gray_benefit is None:
                    green_to_gray_benefit= list(self.benefit_lid_type.loc[self.benefit_lid_type['lid_type'] == lid.lid_process.lid_type, 'green_to_gray_benefit'])[0]
                else:
                    green_to_gray_benefit=kwargs[self.green_to_gray_benefit.name]
                
                if self.park_benefit is None:
                    park_benefit= list(self.benefit_lid_type.loc[self.benefit_lid_type['lid_type'] == lid.lid_process.lid_type, 'park_benefit'])[0]
                else:
                    park_benefit=kwargs[self.park_benefit.name]
                
                if self.GI_efficacy is None:
                    GI_efficacy= list(self.benefit_lid_type.loc[self.benefit_lid_type['lid_type'] == lid.lid_process.lid_type, 'GI_efficacy'])[0]
                else:
                    GI_efficacy=kwargs[self.GI_efficacy.name]
                
                total_discounted_cobenefits = total_discounted_cobenefits + self.calculate_cobenefits(lid.number, lid.area, discount_rate, plan_horizon, green_to_gray_benefit, park_benefit, GI_efficacy)

        return total_discounted_cobenefits
        


