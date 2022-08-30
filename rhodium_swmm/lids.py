from dataclasses import dataclass
from os import name
from typing import Any, List
from .swmm_input_element import SWMM_INPUT_ELEMENT_TYPE, SwmmInputElement
from .parameters import RhodiumParameter
import math

class Layer(SwmmInputElement):
    
    def __init__(self, *args) -> None:
        if self.order[0] != "name":
            raise Exception

        for i in range(len(args)):
            if i < len(self.order) - 1:
                setattr(self, self.order[i+1], args[i])
        super().__init__()

class SurfaceLayer(Layer):
    name = "SURFACE"
    order= ["name", "berm_height", "veg_fraction", "surface_roughness", "surface_slope", "extra"]

    def __init__(self, *args) -> None:
        super().__init__(*args)

class PavementLayer(Layer):
    name = "PAVEMENT"
    order= ["name", "thickness", "void_ratio", "imperv_fraction", "permeability", "clog_factor", "regeneration_interval", "regeneration_fraction"]

    def __init__(self, *args) -> None:
        super().__init__(*args)

class SoilLayer(Layer):
    name = "SOIL"
    order=["name", "thickness", "porosity", "field_capacity", "wilting_point", "conductivity", "conductivity_slope", "suction_head"]

    def __init__(self, *args) -> None:
        super().__init__(*args)


class StorageLayer(Layer):
    name = "STORAGE"
    order = ["name", "thickness","void_ratio","seepage_rate","clog_factor"]

    def __init__(self, *args) -> None:
        super().__init__(*args)


class DrainLayer(Layer):
    name = "DRAIN"
    order=["name", "flow_coeff", "flow_exponent", "offset", "open_level", "close_level", "control_curve"]

    def __init__(self, *args) -> None:
        super().__init__(*args)


class DrainageMatLayer(Layer):
    name = "DRAINAGEMAT"
    order=["name", "thickness", "void_frac", "roughness" ]
    def __init__(self, *args ) -> None:
        super().__init__(*args)

@dataclass
class LidControl(SwmmInputElement):
    name: str
    layers: Any

    order = ["name", "lid_type"]
    lid_type = "UNDEFINED"

    def update_swmm_input_dict(self, input: dict) -> dict:
        lid_control_lines = input["LID_CONTROLS"]["lines"]
        lid_control_lines.append(self.gen_input_line())

        for l in self.layers:
            line = [self.name] + l.get_swmm_input_line()
            lid_control_lines.append(l.gen_input_line(line))

        return input

class BioretentionCell(LidControl):
    lid_type = "BC"
    #NT: make the area adjustment after adding bioretention?
    #NT: make sure Rhodium is not setting more GI than the ipervious area of the subcathment

class InfiltrationTrench(LidControl):
    lid_type = "IT"

class RainBarrel(LidControl):
    lid_type = "RB"

class PermeablePavement(LidControl):
    lid_type = "PP"

@dataclass
class LidUsage(SwmmInputElement):
    subcatchment: Any
    lid_process: LidControl
    number: SWMM_INPUT_ELEMENT_TYPE
    area: SWMM_INPUT_ELEMENT_TYPE
    width: SWMM_INPUT_ELEMENT_TYPE
    initSat: SWMM_INPUT_ELEMENT_TYPE
    fromImp: SWMM_INPUT_ELEMENT_TYPE
    toPerv: SWMM_INPUT_ELEMENT_TYPE
    rptFile: SWMM_INPUT_ELEMENT_TYPE
    drainTo: SWMM_INPUT_ELEMENT_TYPE
    fromPerv: SWMM_INPUT_ELEMENT_TYPE

    order = ["subcatchment", "lid_process", "number", "area", "width", "initSat", "fromImp", "toPerv", "rptFile", "drainTo", "fromPerv"]

    def __post_init__(self):
        self.number = int(self.number)
        self.area = float(self.area)

    def update_swmm_input_dict(self, input: dict) -> dict:
        input["LID_USAGE"]["lines"].append(self.gen_input_line())
        return input

