import copy
import logging

from .subcatchments import Subcatchment
from .lids import *
from .swmm import input_reader as sir
from rhodium.model import Model as RhodiumModel
from rhodium import *
from .swmm_problem import swmm_problem

class RhodiumSwmmModel():
    SUPPORTED_LIDS = {
        PermeablePavement.lid_type: PermeablePavement,
        BioretentionCell.lid_type: BioretentionCell,
        InfiltrationTrench.lid_type: InfiltrationTrench,
        RainBarrel.lid_type: RainBarrel
    }

    SUPPORTED_LAYERS = {
        SurfaceLayer.name : SurfaceLayer,
        PavementLayer.name : PavementLayer,
        SoilLayer.name : SoilLayer,
        StorageLayer.name : StorageLayer,
        DrainLayer.name : DrainLayer,
        DrainageMatLayer.name : DrainageMatLayer
    }

    def __init__(self, node_name, swmm_input_file_template=None, subcatchments = {}, lid_controls = {}, lid_usages = [], responses = []) -> None:
        self.subcatchments = subcatchments
        self.lid_controls = lid_controls
        self.lid_usages = lid_usages

        self.start_time = time.perf_counter()
        self.node_name = node_name

        if swmm_input_file_template is not None:
            self.input_template = self.generate_model_from_swmm_input_file(swmm_input_file_template)

        self.rhodium_model = RhodiumModel(swmm_problem)

        self.rhodium_model.responses = responses
        for r in responses:
            self.rhodium_model.uncertainties = self.rhodium_model.uncertainties + r.uncertainties
            self.rhodium_model.levers = self.rhodium_model.levers + r.levers
            self.rhodium_model.parameters = self.rhodium_model.parameters + r.parameters




    def scale_lever(self, obj, parameter, scale_factor, min_range=1, name=""):
        current_value = getattr(obj, parameter)

        lever = None

        if name == "":
            obj_name = getattr(obj, "name", None)
            if obj_name is not None:
                name = "{}_{}".format(obj_name, parameter)

        if name == "":
            subcatchment_name = getattr(obj, "subcatchment", None)
            if subcatchment_name is not None:
                name = "{}_{}".format(subcatchment_name, parameter)

        scale_range = max(current_value * scale_factor, min_range)
        if isinstance(current_value, int):
            scale_range = round(scale_range)
            lever = IntegerLever(name, max(current_value - scale_range, 0), current_value + scale_range)
        else:
            lever = RealLever(name, max(current_value - scale_range, 0), current_value + scale_range)

        setattr(obj, parameter, RhodiumParameter(lever))

    def scale_all_lids(self, parameter, scale_factor, min_range=1, subcatchments=None):
        for lid in self.lid_usages:
            if subcatchments is None or lid.subcatchment in subcatchments:
                self.scale_lever(lid, parameter, scale_factor, min_range=min_range)

    def copy_input_template(self):
        out = self.input_template.copy()
        out['SUBCATCHMENTS'] = copy.deepcopy(out['SUBCATCHMENTS'])
        out['LID_CONTROLS'] = copy.deepcopy(out['LID_CONTROLS'])
        out['LID_USAGE'] = copy.deepcopy(out['LID_USAGE'])

        return out


    def update_rhodium_model(self):
        levers = RhodiumParameter.get_rhodium_levers()
        uncertainties = RhodiumParameter.get_rhodium_uncertainties()
        parameters = RhodiumParameter.get_rhodium_parameters()

        self.rhodium_model.levers = list(levers.values())
        self.rhodium_model.uncertainties = list(uncertainties.values())
        self.rhodium_model.parameters = list(parameters.values())

        self.rhodium_model.constraints = []

        RhodiumParameter.save_all_values()


    def _add_element(self, name, element, location):
        if name in location:
            #print("{} already exists. Skipping.".format(name))
            return False
        else:
            location[name] = element
            return True

    def add_subcatchment(self, subcatchment: Subcatchment):
        return self._add_element(subcatchment.name, subcatchment, self.subcatchments)

    def add_lid_control(self, lid_control: LidControl):
        return self._add_element(lid_control.name, lid_control, self.lid_controls)

    def add_lid_usages(self, lid_usage: LidUsage):
        if lid_usage.lid_process.name not in self.lid_controls:
            print("{} is not defined in lid_controls".format(lid_usage.lid_process.name))
            raise KeyError
        if lid_usage.subcatchment.name not in self.subcatchments:
            print("{} is not defined in subcatchments".format(lid_usage.subcatchment.name))
            raise KeyError

        self.lid_usages.append(lid_usage)
        return True

    def filter_lids_by_subcatchment(self, target_subcatchments: list):
        filtered_lids = []
        for l in self.lid_usages:
            if l.subcatchment.name in target_subcatchments:
                filtered_lids.append(l)

        self.lid_usages = filtered_lids

    def find_replace(self, sections, find, replace, count=None):
        found_count = 0
        for section in sections:
            for line in self.input_template[section]["lines"]:
                for i in range(len(line["values"])):
                    if line["values"][i] == find:
                        line["values"][i] = replace
                        found_count += 1
                        if count is not None and found_count >= count:
                            return

    def add_subcatchments_from_swmm_input_file(self, subcatchment_lines: list):
        for line_dict in subcatchment_lines:
            line = line_dict["values"]
            if len(line) == 0:
                continue
            line = dict(enumerate(line))

            s = Subcatchment(line.get(0), line.get(1), line.get(2), line.get(3), line.get(4), line.get(5), line.get(6), line.get(7), None)

            self.add_subcatchment(s)

    def add_lid_controls_from_swmm_input_file(self, lid_controls_lines: list):
        name = ""
        lid_type = None
        layers = []

        for line_dict in lid_controls_lines:
            line = line_dict["values"]
            if len(line) < 2:
                continue

            # New Lid Control
            if line[0] != name:
                if name != "" and lid_type is not None:
                    lid_constructor = self.SUPPORTED_LIDS.get(lid_type)
                    if lid_constructor is None:
                        raise InvalidSwmmInputFileError
                    self.add_lid_control(lid_constructor(name, layers))
                name = line[0]
                lid_type = line[1]
                layers = []
            # Not a new name, so this must be a layer
            else:
                layer_constructor = self.SUPPORTED_LAYERS.get(line[1])
                if layer_constructor is None:
                    raise InvalidSwmmInputFileError
                line = line[2:]

                layers.append(layer_constructor(*line))

        if name != "" and lid_type is not None:
            lid_constructor = self.SUPPORTED_LIDS.get(lid_type)
            if lid_constructor is None:
                raise InvalidSwmmInputFileError
            self.add_lid_control(lid_constructor(name, layers))

    def add_lid_usages_from_swmm_input_file(self, lid_usages_lines: list):
        for line_dict in lid_usages_lines:
            line = line_dict["values"]
            if len(line) == 0:
                continue

            lid_process = self.lid_controls.get(line[1])
            if lid_process is None:
                raise InvalidSwmmInputFileError

            line = dict(enumerate(line))
            l = LidUsage(line.get(0), lid_process, line.get(2), line.get(3), line.get(4), line.get(5), line.get(6), line.get(7), line.get(8), line.get(9), line.get(10))
            self.lid_usages.append(l)


    def generate_model_from_swmm_input_file(self, file_path):
        input_template = sir.read_swmm_input_file_to_dict(file_path)

        self.add_lid_controls_from_swmm_input_file(input_template["LID_CONTROLS"]["lines"])

        self.add_subcatchments_from_swmm_input_file(input_template["SUBCATCHMENTS"]["lines"])

        self.add_lid_usages_from_swmm_input_file(input_template["LID_USAGE"]["lines"])

        input_template["LID_CONTROLS"]["lines"] = []
        input_template["SUBCATCHMENTS"]["lines"] = []
        input_template["LID_USAGE"]["lines"] = []

        return input_template

    def update_swmm_input_dict_with_model(self, input_dict):
        for lid_control in self.lid_controls.values():
            lid_control.update_swmm_input_dict(input_dict)

        for subcatchment in self.subcatchments.values():
            subcatchment.update_swmm_input_dict(input_dict)

        for lid_usage in self.lid_usages:
            lid_usage.update_swmm_input_dict(input_dict)

        return input_dict

    def max_lids_per_subcatchment(self, subcatchment, area):
        s = self.subcatchments[subcatchment]
        sc_percentImpervious = float (self.subcatchments[subcatchment].percentImperv)
        subcatchment_impervious_area = (float (self.subcatchments[subcatchment].area)*43560)*(sc_percentImpervious/float(100))
        return math.floor(subcatchment_impervious_area/area)

    def check_lid_excess(self):
        for lid in self.lid_usages:
            # check if number is too high
            sc_percentImpervious = float (self.subcatchments[lid.subcatchment].percentImperv)
            subcatchment_area = float (self.subcatchments[lid.subcatchment].area)*43560
            lid_area = float (lid.area)
            lid_number = int (lid.number)

            if lid_number == 0:
                continue

            upper_bound = math.floor(float((sc_percentImpervious/float(100))*subcatchment_area)/(lid_area))
            if upper_bound < 0:
	            upper_bound = 0 
            
            if lid.subcatchment == "Parking_966-2":
                print ("sc_percentImpervious = ", sc_percentImpervious)
                print ("subcatchment_area = ", subcatchment_area)
                print ("lid_area = ", lid_area)
                print ("lid_number =", lid_number)
                print ("float((sc_percentImpervious/float(100)) = ", float((sc_percentImpervious/float(100))))
                print ("upper_bound=", math.floor(float((sc_percentImpervious/float(100))*subcatchment_area)/(lid_area)))


            if lid_number > upper_bound:
                if isinstance(lid.number, RhodiumParameter):
                    lid.number.value = upper_bound
                else:
                    lid.number = upper_bound
                #print ("Rhodium input for subcat {0} had too many lid units, changing to max number {1}".format(self.subcatchments[lid.subcatchment].name, lid.number))

class Error(Exception):
    pass


class InvalidSwmmInputFileError(Error):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

        self.message = "The SWMM input file is invalid"
