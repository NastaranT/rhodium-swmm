import pandas as pd
from pandas.io.parsers import read_csv

#this function creates three spatial priority scores for each subcatchments
# 1: vacant percentage
# 2: aggregation priority
# 3: issue priority

def create_priority_dict():

    subcat_info = pd.read_csv ("data/other_data/vacant_info.csv")
    print(subcat_info)

 
    #Issue priority calculation
    #maximize installation in issues RC (subcatchments)

    issue_sc = pd.read_csv ("data/other_data/issue_subcatchments.csv")
    issue_sc_list = issue_sc['Name'].tolist()

    subcat_info['issue_priority'] = 0

    for index, row in subcat_info.iterrows():
        if row["Name"] in issue_sc_list:
            subcat_info.at[index, "issue_priority"] = 2
        else:
            subcat_info.at[index, "issue_priority"] = 1


    #Aggregation Priority Calculation
    #maximize installation in subcatchments with high GI aggregation potential
    
    neighbor_sc = pd.read_csv ("data/other_data/neighboring_subcatchments.csv")
    neighbor_dict = neighbor_sc.groupby('src_Name')['nbr_Name'].apply(list).to_dict()
    print(neighbor_dict)
    sc_vacant_dict = subcat_info.groupby('Name')['vacant_area'].apply(list).to_dict()
    print(sc_vacant_dict)

    def set_value(row_number, assigned_value):
        return assigned_value[row_number]

    subcat_info['neighbor_rcs'] =subcat_info['Name'].apply(set_value, args =(neighbor_dict , ))
    print(subcat_info)

    subcat_info['aggregation_priority'] = 1


    for index, row in subcat_info.iterrows():
        print (index)
        for rc in row['neighbor_rcs']:
            print("rc---", rc)
            for key in sc_vacant_dict:
                print ("key----", key)
                if rc==key:
                    vacant = sc_vacant_dict[key]
                    print ("vacant-------",vacant)
                    if row["vacant_area"] > 1:
                        subcat_info.at[index, "aggregation_priority"] = 2
                    if row["vacant_area"] > 1 and vacant[0] > 1:
                        subcat_info.at[index, "aggregation_priority"] = 3

    print(subcat_info)

    aggregation_priority_dict = dict(zip(subcat_info.Name, subcat_info.aggregation_priority))
    vacant_priority_dict = dict(zip(subcat_info.Name, subcat_info.percent_vacant))
    issue_priority_dict = dict(zip(subcat_info.Name, subcat_info.issue_priority))

    return (aggregation_priority_dict, vacant_priority_dict, issue_priority_dict)

print (create_priority_dict())
