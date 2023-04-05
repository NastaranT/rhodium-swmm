"""Console script for negley_run."""
from urllib import response
import click
import logging
from rhodium import load, Brush, cache
from platypus.evaluator import PoolEvaluator
from platypus.mpipool import MPIPool
from .platypus_modifications import ProcessPoolEvaluatorWithInit
from .rhodium_analysis import max_each_subcatchment, rhodium_swmm_evaluate, rhodium_swmm_evaluate_robustness, rhodium_swmm_optimize, rhodium_swmm_optimize_borg, rhodium_swmm_optimize_borg, rhodium_swmm_parallel_plot, rhodium_swmm_prim, rhodium_swmm_robust_optimize, hypervolume_test
from rhodium.config import RhodiumConfig
from .config import RhodiumSwmmConfig
import sys
import os
import datetime
import random
from mpi4py import MPI

@click.group()
@click.option("--reuse", is_flag=True, help="Reuse the results in the current directory if available")
@click.option("--num_processes", default = 20, type=int, help="Set the number of processes to use for the simulation. By default this is set to the number of cores on the machine")
@click.option("--log_output", default="platypus.log", type=str, help="File to write log output. Default is rhodium_swmm.log")
@click.option("--log_level", default="INFO", type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERORR', 'CRITICAL']), help="Set logging level")
@click.option("--mpi", is_flag = True, help="Use MPI")
@click.pass_context
def cli(ctx, reuse, num_processes, log_output, log_level, mpi):
    """Console script for negley_run."""
    ctx.ensure_object(dict)

    if num_processes != 1:
        if num_processes < 1:
            num_processes = None
        if mpi==True:
            pool = MPIPool()
            if not pool.is_master():
                RhodiumSwmmConfig.parallel_initialize()
                pool.wait()
                sys.exit()
            RhodiumConfig.default_evaluator = PoolEvaluator(pool)
        else:
            RhodiumConfig.default_evaluator = ProcessPoolEvaluatorWithInit(num_processes, RhodiumSwmmConfig.parallel_initialize)

    log_level = getattr(logging, log_level)
    #logging.basicConfig(filename=log_output, level=logging.INFO)

    if reuse is False:
        now = "{}".format(datetime.datetime.now())
        os.mkdir(now)
        os.chdir(now)
    return 0

#command optimize
@cli.command()
@click.option("--NFE", default=100, type=int, help="Number of optimization runs to perform. Default is 1000.")
@click.option("--algorithm", default="NSGAII_mod", type=click.Choice(['NSGAII_mod']), help="Optimization algorithm. Default is NSGAII.")
def optimize(algorithm, nfe):
    return rhodium_swmm_optimize(algorithm, nfe)

#command hyper-test
@cli.command()
@click.option("--NFE", default=1000, type=int, help="Number of optimization runs to perform. Default is 1000.")
def hypervolume(nfe):
    return hypervolume_test()

#command optimize_borg
@cli.command()
@click.option("--NFE", default=100, type=int, help="Number of optimization runs to perform. Default is 1000.")
@click.option("--epsilons", default=0.02, type=float, help="epsilon")
@click.option("--algorithm", default="BorgMOEA", type=click.Choice(['BorgMOEA']), help="Optimization algorithm. Default is BorgMOEA.")
def optimize_borg(algorithm, nfe, epsilons):
    return rhodium_swmm_optimize_borg(algorithm, nfe, epsilons)



#command robust-optimize
@cli.command()
@click.option("--NFE", default=1000, type=int, help="Number of optimization runs to perform. Default is 1000.")
@click.option("--algorithm", default="NSGAII_mod", type=click.Choice(['NSGAII_mod']), help="Optimization algorithm. Default is NSGAII.")
@click.option("--num_SOW", default=100, type=click.IntRange(1,None), help="Set the number of states of the world. Default is 100.")
def robust_optimize(num_sow, algorithm, nfe):
    return rhodium_swmm_robust_optimize(num_sow=num_sow, algorithm=algorithm, NFE=nfe)

#command evaluate
def find_policy(output_filename, method, response):
    output = load(output_filename)[1]

    if method == "min":
        policy = output.find_min(response)
    elif method == "max":
        policy = output.find_max(response)
    else:
        raise Exception

    return policy
    

@cli.command()
@click.option("--num_SOW", default=100, type=click.IntRange(1,None), help="Set the number of states of the world. Default is 100.")
@click.option("--optimize_output", type=click.Path(exists=True), help="Output csv from Rhodium-SWMM optimization")
@click.option("--policy", type=(click.Choice(['min', 'max']), str), default=("min", "RunoffVolume"), help="Takes a response name followed by either min or max. Finds a policy that minimizes or maximizes the specified response.")
def evaluate(num_sow, optimize_output, policy):
    method, response = policy
    return rhodium_swmm_evaluate(find_policy(optimize_output, method, response), num_sow=num_sow)

#command evaluate_robustness
@cli.command()
@click.option("--num_SOW", default=100, type=click.IntRange(1,None), help="Set the number of states of the world. Default is 100.")
@click.option("--optimize_output", type=click.Path(exists=True), help="Output csv from Rhodium-SWMM optimization")
def evaluate_robustness(num_sow, optimize_output):
    output = load(optimize_output)[1]
    policies = cache("policies_mordm", lambda: output)
    return rhodium_swmm_evaluate_robustness(policies, num_sow=num_sow)



#command parallel_plot
def generate_brush(response, cutoff):
    return [Brush("{response} > {cutoff}".format(response=response, cutoff=cutoff)), 
            Brush("{response} <= {cutoff}".format(response=response, cutoff=cutoff))]

@cli.command()
@click.option("--optimize_output", type=click.Path(exists=True), help="Output csv from Rhodium-SWMM optimization")
@click.option("--response", type=str)
@click.option("--cutoff", type=float)
def parallel_plot(optimize_output, response, cutoff):
    output = load(optimize_output)[1]
    return rhodium_swmm_parallel_plot(output, generate_brush(response, cutoff))

#command prim
def generate_classification(response, cutoff, tag1, tag2):
    return "'{tag1}' if {response} < {cutoff} else '{tag2}'".format (tag1=tag1, response=response, cutoff=cutoff, tag2=tag2)

@cli.command()
@click.option("--evaluate_output", type=click.Path(exists=True), help="Output csv from Rhodium-SWMM optimization")
@click.option("--response", type=str)
@click.option("--cutoff", type=float)
@click.option("--tag1", type=str, help="should choose between 'good' or 'bad' when is less than a cutoff value")
@click.option("--tag2", type=str, help="should choose between 'good' or 'bad' when is greater than a cutoff value")
def prim(evaluate_output, response, cutoff, tag1, tag2):
    results = load(evaluate_output)[1]
    classification= results.apply(generate_classification(response, cutoff, tag1, tag2))
    return rhodium_swmm_prim(results, classification )

@cli.command()
def runswmm():
    return max_each_subcatchment()

# #command sensitivity analysis
# @cli.command()
# @click.option("--optimize_output", type=click.Path(exists=True), help="Output csv from Rhodium-SWMM optimization")
# @click.option("--response", type=str, help="name of the response of interest")
# @click.option("--policy", type=(click.Choice(['min', 'max']), str), default=("min", "RunoffVolume"), help="Takes a response name followed by either min or max. Finds a policy that minimizes or maximizes the specified response.")
# @click.option("--sensitivity_method", type=str, help="name of the sensitivity method")
# @click.option("--nsamples", default=100, type=int, help="number of samples for sensitivity analysis")
# def sensitivity_analysis(optimize_output,policy, response, sensitivity_method, nsamples):
#     method, response = policy
#     return rhodium_swmm_sensitivity_analysis( find_policy(optimize_output, method, response), response=response, sensitvity_method=sensitivity_method, nsamples=nsamples)




if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
