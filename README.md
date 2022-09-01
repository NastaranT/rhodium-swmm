Rhodium-SWMM
=======

**Rhodium-SWMM** is a Python library for green infrastructure placement under deep uncertainty.

Module Summary
--------------

* **model&#46;py** - Defines the RhodiumSwmmModel class and provides utilities for manipulating it.
* **swmm_problem.py** - Defines the function used for model evaluation in Rhodium.
* **swmm_input_element.py** - Defines a SwmmInputElement. This can be any LID control, LID usage, or subcatchment in a SWMM input file.
* **parameters&#46;py** - Defines the RhodiumParameter class.  This class can be substituted for any SwmmInputElement or the element's fields (e.g. area or number of a LID usage) to turn it into a lever or uncertainty in Rhodium.
* **subcatchment&#46;py** - Defines the Subcatchment class, a type of SwmmInputElement representing subcatchments in a SWMM input file.
* **lids&#46;py** - Defines classes relating to LIDs. Each is a type of SwmmInputElement representing LIDs in a SWMM input file.
* **response &#46;py** - An extension of the Rhodium Response class with extra functionality to calculate the value of the response in the swmm_problem function (swmm_problem.py).
* **uncertainties&#46;py** - Part of work in progress upgrades to how rainfall uncertainty is integrated.
* **cli&#46;py** - Defines the command line interface for negley_run
* **rhodium_analysis.py** - Runs the Rhodium analysis 
* **config&#46;py** - RhodiumSwmmConfig class 
* **example_module** - has the data and code for running a stylized problem 

<br>
<br>



## Tebyanian-etal_2022_Environmental Modelling & Software

**Rhodium-SWMM: An Open-Source Tool for Green Infrastructure Placement Under Deep Uncertainty**

Nastaran Tebyanian<sup>1,2,3\*</sup> , Jordan Fischbach <sup>2</sup> , Robert Lempert<sup>3</sup> , Hong Wu<sup>4</sup> , Debra Knopman<sup>3</sup> , Lisa Iulo<sup>1</sup> , and Klaus Keller<sup>5</sup> 

<sup>1 </sup> Department of Architecture, The Pennsylvania State University, University Park, PA, USA

<sup>2 </sup> The Water Institute of the Gulf, Baton Rouge, LA, USA

<sup>3 </sup> RAND Corporation, Pittsburgh, PA, USA

<sup>4 </sup> Department of Landscape Architecture, The Pennsylvania State University, University Park,
PA, USA

<sup>5 </sup> Thayer School of Engineering at Dartmouth College, Hanover, NH, USA


\* corresponding author:  ntebyanian@thewaterinstitute.org

## Abstract
Green Infrastructure (GI) measures are increasingly used for climate adaptation in urban areas. Designing GI portfolios and evaluating their effectiveness still poses nontrivial challenges given the deep uncertainties and the need to navigating tradeoffs between multiple objectives. Many-objective Robust Decision Making (MORDM) have proven useful in informing this kind of design problems, but thus far, MORDM has been sparsely used for GI design.

To help mainstream MORDM applications in GI planning, we developed an open-source Python library, Rhodium-SWMM, for GI planning under deep uncertainty. Rhodium-SWMM connects the USEPA’s Stormwater Management Model (SWMM) to Rhodium, a Python library for MORDM. It provides a generalizable and flexible interface for taking SWMM input files and setting up a multi-objective optimization problem with the ability to define a wide range of parameters in the SWMM input file as uncertainties or levers. This opens up opportunities to more conveniently analyze new research questions and applications involving multi-scale GI placement under deep uncertainty.


## Journal reference
Coming soon

## Code reference
Tebyanian, Nastaran. “NastaranT/Rhodium-Swmm: Rhodium-SWMM Version 1.0 Initial Release.” Zenodo, August 31, 2022. https://doi.org/10.5281/ZENODO.7038551.


## Data 
The subfolders of data for the stylized problem are described below. The data folder is located in `/example/example_module/data/`.

### Input data
swwm_data
* Sample SWMM input file is locatetd in data/swmm_data/swmm_input_template/Site_Drainage_Model.inp. The data is included with installation of SWMM 5.2.1.   
US EPA. (2022). Storm Water Management Model (SWMM) (5.2.1). https://www.epa.gov/water-research/storm-water-management-model-swmm

other_data
* Stylized subcatchment information data was generated and are located in data/other_data (including subcatchment vacant percentage and area (_vavcant_info.csv_), neighboring subcatchments of each subcatchment (_neighboring_subcatchments.csv_) and subcatchments with community reported issues (_issue_subcatchments.csv_))
* Shapefile of the study area (_example.shp, example.shx, example.dbf_)


cost_benefit
* Data on cost and benefits parameters of bioretention cells are generated from literature review (_cost_lid_type.csv_ and _benefit_lid_type.csv_)

 
### Output data
other_data

* Output of the multiobjective optimization described in the paper (_optimize-NSGAII-100000-3obj.csv_)


## Reproduce the stylized problem and use Rhodium_SWMM for your data
Please see `README.md` in `/example/example_module/` to run Rhodium_SWMM example analysis and see recommendations for applying to your data. 
