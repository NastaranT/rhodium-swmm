import pandas as pd
import geopandas as gpd
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import contextily



optimize_output =  pd.read_csv ("../data/other_data/optimize-NSGAII-100000-3obj.csv")
optimize_output = optimize_output.T
optimize_output.reset_index(inplace=True)
optimize_output = optimize_output.rename(columns = {'index':'Name'})

num_cols = len(list(optimize_output))
rng = range(0, (num_cols)+1 )
new_cols = ['num_br_' + str(i) for i in rng] 
# ensure the length of the new columns list is equal to the length of df's columns
optimize_output.columns = new_cols[:num_cols]
optimize_output = optimize_output.rename(columns = {'num_br_0':'Name'})
print (optimize_output)


## finding solutions with min and max in each objective 
#getting the values of the three objectives (last three rows)
metric_df = optimize_output.tail(3)
print(metric_df)

metric_df.set_index('Name', inplace=True)
metric_df['lowest_col'] = metric_df.idxmin(axis=1)
metric_df['highest_col'] = metric_df.iloc[:,:-1].idxmax(axis=1)
print(metric_df['lowest_col'])
print(metric_df['highest_col'])


##removing _num_br from the end of NAME of each subcatchment
optimize_output["Name"] = optimize_output["Name"].str[:-7]
print (optimize_output)
optimize_output = optimize_output.iloc[:-3]
print (optimize_output)

## converting number of bioretentions to bioretention area in acre
optimize_output_area = optimize_output.drop( 'Name', axis=1).apply (lambda x : (x*40)/43560)
optimize_output_area['Name']= optimize_output['Name']
print(optimize_output_area)
    
swmm_shapefile = gpd.read_file("../data/other_data/example.shp")
print(swmm_shapefile)

## merge the subcatchment with the optimizarion results
results_shape = swmm_shapefile.merge(optimize_output_area, left_on="Name", right_on="Name")
print(results_shape.head())
results_shape['imp_area'] = results_shape['Area']*results_shape['Prc_Imp']
col = results_shape.loc[: , "num_br_1":"num_br_100"]
results_shape['num_br_average'] = (col.mean(axis=1))
results_shape['num_br_average_to_imp_area']=(results_shape['num_br_average']/results_shape['imp_area'])*100
results_shape['num_br_2_to_imp_area']=(results_shape['num_br_2']/results_shape['imp_area'])*100

#ax=rc_results_shape.plot( 'num_br_average', edgecolor='gray',scheme="User_Defined", legend=True, cmap= 'RdPu',classification_kwds=dict(bins=[0,25,50,75,100]), norm=Normalize(0, 4 ), alpha=1)
#ax=rc_results_shape.plot( 'num_br_2_to_imp_area', edgecolor='gray',scheme="User_Defined", legend=True, cmap= 'RdPu',classification_kwds=dict(bins=[0,25,50,75,100]), norm=Normalize(0, 4 ), alpha=1)
ax=results_shape.plot( 'num_br_2_to_imp_area', edgecolor='gray',scheme="NaturalBreaks", legend=True, cmap= 'RdPu', alpha=1)
#ax=results_shape.plot( 'num_br_2_to_imp_area', edgecolor='gray',scheme="NaturalBreaks", legend=False, cmap= 'RdPu', alpha=1)
print(results_shape['num_br_2_to_imp_area'])
# contextily.add_basemap (
#     ax=ax,
#     crs=rc_results_shape.crs, 
#     source=contextily.providers.Stamen.TonerLite,
# )

plt.show()

