"""Main module."""
from distutils.file_util import write_file
import logging
import os
from rhodium import *
from rhodium.config import RhodiumConfig
from rhodium_swmm import subcatchments
from .platypus_modifications import ProcessPoolEvaluatorWithInit

from rhodium_swmm.swmm_problem import swmm_problem, max_subcatchment
from .config import RhodiumSwmmConfig
from platypus import Hypervolume, calculate, display, experiment
from rhodium.optimization import _to_problem
from platypus.algorithms import NSGAII, NSGAIII
from .platypus_modifications import NSGAII_mod
import csv

def rhodium_swmm_optimize(algorithm="NSGAII_mod", NFE=1000, output_filename=None):
    if output_filename is None:
        output_filename = "optimize-{}-{}.csv".format(algorithm, NFE)

    rhodium_swmm_model=RhodiumSwmmConfig.initialize()
    np.random.seed(1234)
    output = optimize(rhodium_swmm_model.rhodium_model, algorithm, NFE, log_frequency=1, population_size=100, module="rhodium_swmm.platypus_modifications")
    output.save(output_filename, format="csv")

    os.system("rm -rf */")

def hypervolume_test (algorithm=[NSGAII_mod], NFE=1000, SEEDS=3,output_filename=None):
    if output_filename is None:
        output_filename = "experiment-{}-{}.txt".format(algorithm, NFE)

    rhodium_swmm_model=RhodiumSwmmConfig.initialize()
    problem, levers = _to_problem(rhodium_swmm_model.rhodium_model)
    
    with ProcessPoolEvaluatorWithInit(20, RhodiumSwmmConfig.parallel_initialize) as evaluator:
        results = experiment(algorithm, [problem], nfe=NFE, seeds=SEEDS, evaluator=evaluator)
        #print(results)
        

        keys, values = [], []

        for key, value in results.items():
            keys.append(key)
            print(keys)
            values.append(value)
            print(len(value["Problem"]))
            print("TTTTTTTTTTTTTTTTTTTTT")
            print(len(value["Problem"][0]))
        reference_set = []
        for solution in results["NSGAII"]["Problem"]:
            reference_set.extend(solution)            

        # with open("results.csv", "w") as outfile:
        #     csvwriter = csv.writer(outfile)
        #     csvwriter.writerow(keys)
        #     csvwriter.writerow(values)
        hyp = Hypervolume(reference_set=reference_set)
        #hyp = Hypervolume(minimum=[0, 0], maximum=[102000000, 1.61])
        hyp_result = calculate(results, hyp, evaluator=evaluator)
        print(hyp_result)
        display(hyp_result, ndigits=6)



def rhodium_swmm_optimize_borg(algorithm="BorgMOEA", NFE=100, epsilons=0.02,output_filename=None):
    if output_filename is None:
        output_filename = "optimize-{}-{}-{}.csv".format(algorithm, NFE, epsilons)

    rhodium_swmm_model=RhodiumSwmmConfig.initialize()

    output = optimize(rhodium_swmm_model.rhodium_model, algorithm, NFE,epsilons=epsilons, module="pyborg", log_frequency=1)
    output.save(output_filename, format="csv")

def rhodium_swmm_robust_optimize(num_sow=100, algorithm="NSGAII_mod", NFE=1000):
    rhodium_swmm_model=RhodiumSwmmConfig.initialize()

    #SOWs = sample_lhs(rhodium_swmm_model.rhodium_model, num_sow)
    #SOWs.save("sow.csv", format="csv")
    SOWs = load("data/other_data/SOW12.csv", format="csv")[1]
    output = robust_optimize(rhodium_swmm_model.rhodium_model, SOWs, algorithm, NFE, module="rhodium_swmm.platypus_modifications")
    output.save("robust_optimize.csv", format="csv")

def rhodium_swmm_evaluate(policy, num_sow=100):
    rhodium_swmm_model=RhodiumSwmmConfig.initialize()

    SOWs = sample_lhs(rhodium_swmm_model.rhodium_model, num_sow)
    #SOWs = load("data/other_data/SOW6-90.csv", format="csv")[1]
    SOWs.save("sow.csv", format="csv")
    

    results = evaluate(rhodium_swmm_model.rhodium_model, update(SOWs, policy))
    results.save("evaluate_policy.csv", format="csv")

def rhodium_swmm_evaluate_robustness(policies, num_sow=100):
    rhodium_swmm_model=RhodiumSwmmConfig.initialize()

    SOWs = sample_lhs(rhodium_swmm_model.rhodium_model, num_sow)
    SOWs.save("sow.csv", format="csv")


    results = cache("robustness", lambda : evaluate_robustness(rhodium_swmm_model.rhodium_model, policies, SOWs))
    results.save("evaluate_robustness.csv", format="csv")


def rhodium_swmm_parallel_plot(optimize_output, brush):
    rhodium_swmm_model=RhodiumSwmmConfig.initialize()
    #optimize_output = load("data/result_to_viz/optimize-NSGAII-100000.csv.csv", format="csv")[1]
    fig = parallel_coordinates(rhodium_swmm_model.rhodium_model, optimize_output,brush=brush)
    #plt.savefig("parallel_plot.png")
    plt.show()

def rhodium_swmm_prim (results, classification):
    rhodium_swmm_model=RhodiumSwmmConfig.initialize()

    p = Prim(results, classification, include=rhodium_swmm_model.rhodium_model.uncertainties.keys(),coi="good")
    box = p.find_box()
    #write_file(box, "prim_box.txt")
    fig1 = box.show_tradeoff()
    #plt.savefig("prim_tradeoffs.png")
    fig2= box.show_details()
    #plt.savefig("prim_details.png")
    plt.show()

def max_each_subcatchment():
    rhodium_swmm_model=RhodiumSwmmConfig.initialize()

    f = open("max_subcat.csv", "w")
    f.write("subcatchment,max_gi,area,percentImperv,peak_flow_rate,average_flow_rate\n")
    with RhodiumConfig.default_evaluator.executor as executor:
        subcatchments = [s for s in rhodium_swmm_model.subcatchments.keys()]

        for result in executor.map(max_subcatchment, subcatchments):
            f.write("{},{},{},{},{},{}\n".format(*result))
            print(result)

        f.close()



# def rhodium_swmm_sensitivity_analysis(policy, response, sensitivity_method="sobol", nsamples=100):
#     rhodium_swmm_model=RhodiumSwmmConfig.initialize()

#     result = sa(rhodium_swmm_model.rhodium_model, response, policy, method=sensitivity_method, nsamples=nsamples)
#     write_file(result, "sensitivity.txt")
#     fig1=result.plot()
#     plt.savefig("sensitivity_results.png")
#     fig2 = result.plot_sobol(threshold=0.01) 
#     plt.savefig("sobol.png")  




