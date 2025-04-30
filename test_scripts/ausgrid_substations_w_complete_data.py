import os
import pandas as pd
import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union
import random


'''
this code goes through the ausgrid data files and determines which 
substations have data present for all years. some substation data is incomplete.
'''


# Set the path to the main directory
path_to_dir = 'ausgrid_data\extracted'

# Create two empty dataframes to store the results
missing_names_df = pd.DataFrame(columns=['name', 'missing_in', 'missing_in_dirs'])
present_names_df = pd.DataFrame(columns=['name', 'present_in'])

# Create a dictionary to store the files with their paths
files_dict = {}

# Loop through all the subdirectories in the main directory
for subdir in os.listdir(path_to_dir):
    subdir_path = os.path.join(path_to_dir, subdir)
    # Check if the current item is a directory
    if os.path.isdir(subdir_path):
        # Loop through all the CSV files in the current directory
        for filename in os.listdir(subdir_path):
            if filename.endswith('.csv'):
                # Get the name of the file (ignoring the _XXXXX.csv suffix)
                name = filename.split('_')[0]
                # Add the file path and directory name to the dictionary
                if name in files_dict:
                    files_dict[name].append((os.path.join(subdir_path, filename), subdir))
                else:
                    files_dict[name] = [(os.path.join(subdir_path, filename), subdir)]

# Loop through the dictionary and check if each file exists in all subdirectories
for name, paths in files_dict.items():
    present_in = set([path[1] for path in paths])
    if len(present_in) == len(os.listdir(path_to_dir)):
        present_names_df = present_names_df.append({'name': name, 'present_in': len(paths)}, ignore_index=True)
    else:
        missing_in = set(os.listdir(path_to_dir)) - present_in
        missing_names_df = missing_names_df.append({'name': name, 'missing_in': len(missing_in), 'missing_in_dirs': ', '.join(missing_in)}, ignore_index=True)

print("Names present in all subdirectories:")
print(present_names_df)
print("\nNames missing in some subdirectories:")
print(missing_names_df)

present_names_df['name'].to_csv('substations_w_complete_data.csv', index = False)

