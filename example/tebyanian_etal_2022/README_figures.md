# Reproduce my experiment and figures
Once you have successfully built your container, 


1. Multiobjective optimization (100,000 NFE)<br>
Run <br> 
`docker run -v <full path to results directory>:/localmnt -u $(id -u ${USER}):$(id -g ${USER}) rhodium_swmm example_module optimize --NFE 100000`
<br>
The multiobjective optimization will run and you will get Pareto set (*optimize-NSGAII-100000.csv*) and all simulation results (*all_results.csv*) in your results directory. The Pareto set output is already included (other_data/optimize-NSGAII-100000-3obj.csv)

2. **Parallel plot (Figure 6)** <br>
Place the *optimize-NSGAII-100000.csv* in other_data. <br>
Run <br> 
`docker run -v <full path to results directory>:/localmnt -u $(id -u ${USER}):$(id -g ${USER}) rhodium_swmm example_module parallel-plot --optimize_output ~/example_module/example_module/other_data/optimize-NSGAII-100000-.csv --response “RunoffVolume” --cutoff 25`
<br>
the plot pops up. You can save it in your result directory.

3. **Map of a solution with the least runoff in the Pareto set (Figure 4)** <br>
Place the *optimize-NSGAII-100000.csv* in other_data. <br>
Navigate to the cloned rhodium-swmm folder <br> 
`cd rhodium-swmm/example/example_module/spatial_priorities`
<br>
change the file name in map_viz.py to optimize-NSGAII-100000-.csv* . Run <br>
`python map_viz.py`
<br>
the map pops up. You can save it in your result directory.

4. **PRIM analysis/plots (Figure A3)** <br>
Place the *optimize-NSGAII-100000.csv* in other_data <br>
Run <br> 
`docker run -v <full path to results directory>:/localmnt -u $(id -u ${USER}):$(id -g ${USER}) rhodium_swmm example_module evaluate –num_SOW 100  –optimize-output ~/example_module/example_module/other_data/optimize-NSGAII-100000-.csv  –policy min RunoffVolume`
<br>
The simulation will run in your result directory and will create "evaluate_policy.csv". Place this file in other_data.
<br>
Run <br> 
`docker run -v <full path to results directory>:/localmnt -u $(id -u ${USER}):$(id -g ${USER}) rhodium_swmm example_module prim --evaluate_output ~/example_module/example_module/data/other_data/evaluate_policy.csv --response "Cost" --cutoff 2500000 --tag1 "good" --tag2 "bad"`
<br>
the plots pop up. You can save them in your result directory.

5. **3D and 2D plots (Figure 5 and A2)** <br>
We created these plots with tradeoff_plots.R. You can use the Pareto set (*optimize-NSGAII-100000.csv*) and all simulation results (*all_results.csv*) to reproduce the figures<br>

