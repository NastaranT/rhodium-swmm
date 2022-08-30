from dataclasses import dataclass
import dataclasses
from math import floor, sqrt
from typing import List

from rhodium_swmm.lids import LidUsage

from .parameters import RhodiumParameter
from .swmm_input_element import SwmmInputElement, SWMM_INPUT_ELEMENT_TYPE
from .swmm import units

@dataclass
class Subcatchment(SwmmInputElement):
    name: SWMM_INPUT_ELEMENT_TYPE
    rain_gage: SWMM_INPUT_ELEMENT_TYPE
    outlet: SWMM_INPUT_ELEMENT_TYPE
    area: SWMM_INPUT_ELEMENT_TYPE
    percentImperv: SWMM_INPUT_ELEMENT_TYPE
    width: SWMM_INPUT_ELEMENT_TYPE
    slope: SWMM_INPUT_ELEMENT_TYPE
    curb_len: SWMM_INPUT_ELEMENT_TYPE
    snow_pack: SWMM_INPUT_ELEMENT_TYPE = None
    lids: List[LidUsage] = dataclasses.field(default_factory=list)
    units: str = "US"

    order = ["name", "rain_gage", "outlet", "area", "percentImperv", "width", "slope", "curb_len", "snow_pack"]

    def __post_init__(self):
        for l in self.lids:
            l.subcatchment = self

        self.percentImperv = RhodiumParameter(self.percentImperv)

    def update_swmm_input_dict(self, input) -> dict:
        input["SUBCATCHMENTS"]["lines"].append(self.gen_input_line())
        return input


###############################################################################
#
# Code below this line is currently not used
#
###############################################################################

    def remove_lid_from_subcatchment(self, sc_area, width, percent_imperv, lid):
        '''Code for currently unsupported subcatchment area adjustment when modifying lids
        '''
        
        lid_base_sc_area = float(sc_area) * self.units["sc"]
        lid_base_sc_imperv = (float(percent_imperv) * units.registry.percent)
        lid_base_sc_imperv_area = lid_base_sc_imperv * lid_base_sc_area
        lid_num_units = lid.number
        #figure out if there is too much permeable pavement being added - dependent on impervious area
        upper_bound = floor(float((lid_base_sc_imperv_area.to(self.units["lid"]))/(lid.area*self.units["lid"])))
        if upper_bound < 0:
            upper_bound = 0

        excess = int(lid_num_units - upper_bound)
        if excess <= 0:
            excess = 0
        else: 
            print("PP upper bound", upper_bound, " 1:", lid_base_sc_imperv_area.to(self.units["lid"]), " 2: ", (lid.area*self.units['lid']))
            lid.set_attribute("number", lid_num_units - excess)
            print("RHODIUM input for subcat {0} had too many lid units, changing to max number {1}".format(lid.name, lid_num_units))
	
        lid_total_area = lid_num_units * lid.area * self.units['lid']
    
        #adjust subcatchment areas after LIDs are added
        lid_sc_area = lid_total_area.to(self.units['sc'])
        new_lid_base_sc_area = lid_base_sc_area - lid_sc_area
        sc_new_area = new_lid_base_sc_area.magnitude

        
        lid_sc_area_magnitude = lid_sc_area.magnitude

        new_lid_base_sc_imperv_area = lid_base_sc_imperv_area - lid_sc_area
        new_lid_base_sc_imperv = (new_lid_base_sc_imperv_area / new_lid_base_sc_area)

        lid_sc_imperv = 0
        new_imperv = (new_lid_base_sc_imperv.to('percent').magnitude)

        #adjust subcatchment widths
        lid_sc_width = (sqrt(lid_total_area/self.units['lid']))

        lid_sc = Subcatchment(self.name+"##"+lid.lid_process.name, self.rain_gage, self.outlet, lid_sc_area_magnitude, lid_sc_imperv, lid_sc_width, self.slope, self.curb_len, self.snow_pack)
        #New Subcatchment Width = Old Width * Non-LID Area / Original Area
        old_width = float(width)
        new_width = old_width*(float(new_lid_base_sc_area/self.units['sc'])/float(lid_base_sc_area/self.units['sc']))
        return (sc_new_area, new_width, new_imperv, lid_sc)

    def get_updated_area(self):
        '''Code for currently unsupported subcatchment area adjustment when modifying lids
        '''
        area = self.area
        width = self.width
        imperv = self.percentImperv
        new_sc_lids = []
        for lid in self.lids:
            (area, width, imperv, new_lid) = self.remove_lid_from_subcatchment(area, width, imperv, lid)
            new_sc_lids.append(new_lid)

        return (area, width, imperv, new_sc_lids)
    


