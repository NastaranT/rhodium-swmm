"""Common functionality for handling units."""

import pint

registry = pint.UnitRegistry()
"""A UnitRegistry singleton preconfigured with custom rules."""

registry.define('percent = count / 100')

def area_units(input_unit_system):
    """Takes in input unit system and determines area units for
            lid and sc, returns A_units, 
            list of lid area unit and sc area unit"""
    if input_unit_system == 'US':
        lid_area_unit = registry.ft ** 2
        width_unit = registry.ft
        sc_area_unit = registry.acre
    elif input_unit_system == 'SI':
        lid_area_unit = registry.m ** 2
        width_unit = registry.m
        sc_area_unit = registry.hectare
    else:
        raise Exception(
            'Unknown unit system "{0}".'.format(input_unit_system),)
    A_units = {"lid": lid_area_unit,"width": width_unit,"sc": sc_area_unit}
    return A_units
