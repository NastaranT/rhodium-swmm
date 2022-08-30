from abc import ABC
from dataclasses import dataclass
import typing

from pint import set_application_registry

class SwmmInputElement(ABC):

    order = []

    def is_rhodium_parameter(self, value):
        if "rhodium_model_param" in dir(value):
            return True
        return False

    def get_attribute(self, attr):
        if attr not in dir(self):
            return None
        value = getattr(self, attr)
        if self.is_rhodium_parameter(value):
            return value.value
        return value


    def set_attribute(self, attr, new_value):
        value = getattr(self, attr)
        if self.is_rhodium_parameter(value):
            value.value = new_value
            return
        else:
            setattr(self, attr, new_value)

    def update_swmm_input_dict(self, input: dict) -> dict:
        return input

    # def set_class_values_from_swmm_input(self, input):
    #     for i in range(len(self.order)):
    #         self.set_attribute(self.order, input[i])

    def get_swmm_input_line(self):
        l = []
        for attr in self.order:
            value = self.get_attribute(attr)
            if value is not None:
                l.append(value)
        return l

    def gen_input_line(self, values=None, comment="added by RHODIUM_SWMM") -> dict:
        if values is None:
            values = self.get_swmm_input_line()
        return {"values": [str(v) for v in values if v is not None], "comment": comment}

    def __str__(self) -> str:
        return self.name

SWMM_INPUT_ELEMENT_TYPE = typing.Union[str, int, float, SwmmInputElement]