from .input_writer import write_dict_to_swmm_input_file, write_dict_to_swmm_input_string
#import swmm_cached
from pyswmm import swmm5

run_num = 0

def swmm_run_from_inp(node_names, swmm_input_file_path="swmm.inp",binary_output_path="swmm.out", report_output_path=None, swmm_bin_path="runswmm"):

    if report_output_path is None:
        if binary_output_path.endswith('.out'):
            report_base_path = binary_output_path[:-4]
        else:
            report_base_path = binary_output_path
        report_output_path = '{0}.rpt'.format(report_base_path)
    
    swmm_model = swmm5.PySWMM(swmm_input_file_path, report_output_path, binary_output_path)
    swmm_model.swmm_open()
    swmm_model.swmm_start()
    while(swmm_model.swmm_stride(10000) > 0):
        continue
    
    node_sum=0
    for nodename in node_names:
        node = swmm_model.node_statistics(nodename)
        print(node)
        node_sum += node['max_depth']
        #subcat_sum += subcat['peak_runoff_rate']
        print('subcat node_sum----', node_sum)
    
    node_avergae= node_sum/len(node_names)

    swmm_model.swmm_end()
    swmm_model.swmm_close()

    return node_avergae
    #return node_of_interest

def swmm_run_from_string(node_name, swmm_input_file):
    """Used for not yet working in memory SWMM execution
    """
    
    swmm_model = swmm5.PySWMM(swmm_input_file, "report_output_path", "binary_output_path")
    swmm_model.swmm_open()
    swmm_model.swmm_start()
    while(swmm_model.swmm_stride(10000) > 0):
        continue
    outfall = swmm_model.outfall_statistics(node_name)

    swmm_model.swmm_end()
    swmm_model.swmm_close()

    #return node_of_interest
    return outfall

def swmm_run_from_dict(node_names, swmm_input_dict, swmm_input_file_path="swmm.inp",binary_output_path="swmm.out", report_output_path=None, swmm_bin_path="runswmm"):

    write_dict_to_swmm_input_file(swmm_input_dict=swmm_input_dict, swmm_input_file_path=swmm_input_file_path)

    return swmm_run_from_inp(node_names, swmm_input_file_path=swmm_input_file_path, binary_output_path=binary_output_path, report_output_path=report_output_path, swmm_bin_path=swmm_bin_path)

def swmm_run_from_dict_to_str(node_names, swmm_input_dict):
    """Used for not yet working in memory SWMM execution
    """

    swmm_inp_file = write_dict_to_swmm_input_string(swmm_input_dict=swmm_input_dict)

    return swmm_run_from_string(node_names, swmm_input_file=swmm_inp_file)