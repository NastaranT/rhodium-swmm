import time

from .swmm.run import swmm_run_from_dict, swmm_run_from_dict_to_str
from rhodium_swmm.response import RhodiumSwmmResponse
from .parameters import RhodiumParameter


global_model = None


def set_model(m):
    global global_model
    global_model = m

def max_subcatchment(subcatchment):
    swmm_model = global_model
    print("Elapsed time: {} sec".format(time.perf_counter() - swmm_model.start_time))
    RhodiumParameter.restore_all_values()

    input_template = swmm_model.copy_input_template()

    max_gi = 0
    area = 0
    percentImperv = 0
    for lid_usage in swmm_model.lid_usages:
        if lid_usage.subcatchment == subcatchment:
            max_gi = swmm_model.max_lids_per_subcatchment(subcatchment, 40)
            area = swmm_model.subcatchments[lid_usage.subcatchment].area
            percentImperv = swmm_model.subcatchments[lid_usage.subcatchment].percentImperv
            print("setting ", lid_usage.subcatchment, "to ",max_gi)

            lid_usage.number.value = max_gi
    
    swmm_model.check_lid_excess()
    input_template = swmm_model.update_swmm_input_dict_with_model(input_template)
    swmm_binary_results = swmm_run_from_dict(input_template)

    return subcatchment, max_gi, area, percentImperv, swmm_binary_results["peak_flowrate"], swmm_binary_results["average_flowrate"]


def swmm_problem(**kwargs):
    """swmm_problem documentation test.

    A more extended description.

    Args:
        kwargs:  The arguments

    Returns:
        list: Values of the responses
    """
    swmm_model = global_model
    print("Elapsed time: {} sec".format(time.perf_counter() - swmm_model.start_time))
    RhodiumParameter.restore_all_values()

    levers_and_uncertainties = RhodiumParameter.get_levers_and_uncertainties()


    input_template = swmm_model.copy_input_template()

    for (name, value) in kwargs.items():
        if name in levers_and_uncertainties:
            for param in levers_and_uncertainties[name]:
                #print("{key}: {value}".format(key=name, value=value))
                param.value = value
    
    swmm_model.check_lid_excess()
    input_template = swmm_model.update_swmm_input_dict_with_model(input_template)
    #swmm_binary_results = swmm_run_from_dict(swmm_model.node_name, input_template)
    swmm_binary_results = swmm_run_from_dict(swmm_model.node_names, input_template)

    results = []
    for r in swmm_model.rhodium_model.responses:
        if isinstance(r, RhodiumSwmmResponse):
            #if it is not a rhodium response raise an error saying you need to define your problem if you are not using our rhodium swmm reponse
            result = r.calculate(swmm_model, swmm_binary_results, **kwargs)
            results.append(result)
            print(r.name, ": ", result)


    return results