

# Rhodium-SWMM Example

This section provides general instructions for installing Rhodium-Swmm and running several analyses on the example model that is provided in the library.  For the steps needed to replicate the exact results and figures presented in [Rhodium-SWMM: An Open-Source Tool for Green Infrastructure Placement Under Deep Uncertainty], please follow **example/teybanian_etal_2022/README_figures.md**.


# Module Summary

* **initialize&#46;py** - Initializes the rhodium-swmm model by setting levers, responses and uncertainties and sets up directory structure for simulation
* **spatial_priorities.py** - creates a dictionary of subcatchments and their spatial priority scores 
* **data** - Directory containing all data needed for simulation
* **spatial_visualization** - Directory containing code to generate visualizations from sample simulation results

# Usage


## Prerequisite Software

Please install software listed below.

* [Docker](https://docs.docker.com/engine/install/) for your operating system.

**Note** 
If using Linux OS ensure you also complete the [Docker post installation steps](https://docs.docker.com/engine/install/linux-postinstall/) before building your container


## Building Conatiner with Docker

Clone the repository by running the following command. 

    git clone https://github.com/NastaranT/rhodium-swmm.git

If you are unfamiliar with git, download a zip file of the repository by clicking on the green Code button.


<br> Build the docker image while in the root of the example_module repository `rhodium-swmm/`.
       
    docker build -t rhodium_swmm . 


<br>**Note** 
*for Mac OS using Arm-based M1 Chip - Some images do not support the ARM64 architecture. You can add `--platform linux/amd64` to run (or build) an Intel image using emulation.

    docker build --platform linux/amd64 -t rhodium_swmm .

## Running example_module command line
1. Run the example_module command line help utility.  The example_module python module has a command line interface accessed by the example_module command. The following command runs the python module inside the docker container, but redirects all output to the directory you chose for results. Replace <results directory> with the full path of the directory where your output will be stored:
```	 
docker run -v <results directory>:/localmnt -u $(id -u ${USER}):$(id -g ${USER}) rhodium_swmm example_module --help
```
2. To view help for a specific sub command add the help directive after the subcommand.  For example to view optimization help run:
```
docker run -v <results directory>:/localmnt -u $(id -u ${USER}):$(id -g ${USER}) rhodium_swmm example_module optimize --help
```
3. Run other commands by modifying the previous one.  For example, to run an optimization with NFE=100 run this command:
```
docker run -v <results directory>:/localmnt -u $(id -u ${USER}):$(id -g ${USER}) rhodium_swmm example_module optimize --NFE 100
```
**Note**: Windows OS does not need to specify user id. Remove `-u ($id -u ${USER}):$(id -g ${USER})` from call string.

# Using the example_module command line utility

## optimize

Options

```
--NFE INTEGER         Number of optimization runs to perform. Default is 1000.

--algorithm [NSGAII]  Optimization algorithm. Default is NSGAII.
```

Example of command with full options: 

`example_module optimize –NFE 100  –algorithm “NSGAII”`

## robust-optimize

Options

```
--NFE INTEGER            Number of optimization runs to perform. Default is 1000.

--algorithm [NSGAII]     Optimization algorithm. Default is NSGAII.

--num_SOW INTEGER RANGE  Set the number of states of the world. Default is 100
```

Example of command with full options: 

`example_module optimize –NFE 100  –algorithm “NSGAII” – --num_SOW 100`

## parallel-plot

Options

```
--optimize_output PATH  Output csv from Rhodium-SWMM optimization

--response TEXT         name of one the responses (RunoffVolume, Cost, CoBenefit, IssuePriority, VacantPriority, AggregationPriority )

--cutoff FLOAT          a cutoff number of interest
```

Example of command with full options:

`example_module parallel-plot --optimize_output ~/example_module/example_module/data/rother_data/optimize-NSGAII-100000-3obj.csv --response “RunoffVolume” --cutoff 1`


## evaluate

Options

```
--num_SOW INTEGER RANGE    Set the number of states of the world. Default is 100.

--optimize_output PATH     Output csv from Rhodium-SWMM optimization

--policy <CHOICE TEXT>...  Takes a response name followed by either min or max. Finds a policy that minimizes or maximizes the specified response.
```

Example of command with full options: 

`example_module evaluate –num_SOW 100  –optimize-output ~/example_module/example_module/data/other_data/optimize-NSGAII-100000-3obj.csv  –policy min RunoffVolume`

## evaluate-robustness

Options

```
--num_SOW INTEGER RANGE     Set the number of states of the world. Default is 100.

--optimize_output PATH      Output csv from Rhodium-SWMM optimization
```

Example of command with full options: 

`example_module evaluate-robustness –num_SOW 100  –optimize-output ~/example_module/example_module/data/other_data/optimize-NSGAII-100000-3obj.csv.csv`


## prim

Options

```
--evaluate_output PATH    Output csv from Rhodium-SWMM optimization

--response TEXT

--cutoff FLOAT

--tag1 TEXT               should choose between 'good' or 'bad' when is less than a cutoff value

--tag2 TEXT               should choose between 'good' or 'bad' when is greater than a cutoff value
```

`example_module prim --evaluate_output ~/example_module/example_module/data/other_data/evaluate_policy.csv --response "Cost" --cutoff 8000 --tag1 "good" --tag2 "bad"`

<br>

# Importing your data 

The data folder has three sub folders:

* swwm_data
<br> - swmm_input_template
* cost_benefit
* other_data



<br> 1) For your specific problem, you need to place a swmm input file (.inp) in swmm_input_template folder. 
<br> Replace the name of the swmm input template file in initizle.py with your file name. 

<br> 2) replace the CSV file of cost information for the LID types with your information in the cost_benefit folder.
<br> - Keep the file name or adjust the file name in initilize.py. Keep the column names as example files provided.

<br> 3) replace the CSV file of benefit information for the LID types with your information in the cost_benefit folder. 
<br> - Keep the file name or adjust the file name in initilize.py. Keep the column names as example files provided.

<br> 4) replace the shapefile for the SWMM input file in other_data

<br> 5) after running the optimization, place the Pareto set CSV in *other_data* and adjust the file name in *map_viz.py*


<br>
