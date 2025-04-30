import os
import pandas as pd
import zipfile
import re
import shutil
import glob

from logging import info

'''
AusgridLoadData class:

So named (ausgrid_load_data) because this class is specifically for Ausgrid load data. 
The actual competition data and CAISO load data will be different and will need to
be processed in a significantly different manner.

This class contains functions for loading, processing, and concatenating 
load data files from Ausgrid. They are in a specific file format and need to 
be processed specially. See below website for ausgrid data:

https://www.ausgrid.com.au/Industry/Our-Research/Data-to-share/Distribution-zone-substation-data

This data is problematic because not all substations are included in the files for each year.
This may cause problems with data processing. 

The "Punchbowl 33" substation works well and is a good choice to use.

After the csv files are processed, they are read by the TrainingData class
to be cleaned in order to make them suitable for ML model training.
    
'''

class CAISOLoadData:
    def __init__(self, substation_name, file_path, start_date, end_date):
        # self.load_file = load_file
        # self.weather_file = weather_file        
        self.substation_name = substation_name
        self.path = file_path
        self.data = pd.DataFrame()
        self.start_date = start_date
        self.end_date = end_date

       