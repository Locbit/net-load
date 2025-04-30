import datetime
from datetime import datetime

from meteostat import Hourly
from meteostat import Point
import pandas as pd
import pytz
import os

import math


import numpy as np

import time


from netload.imputer import Imputer

'''
WeatherData class:

This class contains functions for retrieving weather data from the online meteostat library
and for saving it to csv files. These files will then be used later along with the grid load
data files in the TrainingData class to be cleaned and maide suitable for ML training.

NOTE: using get_hourly_data() pulls data from the meteostat server. So if you do this
too often, you may get temporarily blocked.


'''

from functools import reduce


class WeatherData:
    def __init__(self, substation_name, model_name, substation_loc, start_date, end_date):
        self.substation_name = substation_name
        self.location = Point(substation_loc[0], substation_loc[1])
        self.start_date = start_date
        self.end_date = end_date
        self.data = pd.DataFrame()
        
        self.model_name = model_name
        
        # get this data and put it to a csv
        self.export_hourly_data_to_csv()
                
        
        self.dataframes_list = list(self.data.values())

        
        imputer = Imputer(self.dataframes_list, resample_interval = '1h')
        self.imputed_data = imputer.process_dataframes()
        
        self.imputed_data.index = self.imputed_data.index.tz_localize('UTC')
    
    

        # df = pd.concat(list(self.data.values()), keys=self.data.keys())
        
        # # if you want a flat index
        # df = df.reset_index(level=0, drop=True)

        # self.weather_data = df 
        
    def get_hourly_data(self):

        data = Hourly(self.location, self.start_date, self.end_date).fetch()
        data = data.drop(columns=['coco', 'tsun', 'snow', 'wpgt', 'pres'])
        # data = data.drop(columns=['coco', 'snow', 'wpgt'])
        data = data.rename_axis('DT')
        
        data = data.dropna(how='all')

        # the precipitation data column is articularly problematic as most of the data
        # is nans, which screws up the imputation process. if you fill those nans with
        # zeros, imputation works properly. this is a problem specific to datasets
        # which contain mostly nans.
        data['prcp'] = data['prcp'].fillna(0)
        
        # need to convert windspeed to radians and normalize
        data['wdirsin'] = np.sin(np.radians(data['wdir']))
        data['wdircos'] = np.cos(np.radians(data['wdir']))

        data['wdirsin'] /= np.abs(data['wdirsin']).max()
        data['wdirsin'] /= np.abs(data['wdirsin']).max()


        # calclate wet bulb temperature
        data['twet'] = data.apply(lambda row: self.calculate_wet_bulb_temp(row['temp'], row['rhum']), axis=1)

        # Calculate the Temperature-Humidity Index and add it as a new column
        data['thi'] = data.apply(lambda row: self.calculate_thi(row['temp'], row['rhum']), axis=1)

        # Assuming your dataframe is called 'df'
        columns_to_keep = ['thi', 'twet', 'prcp', 'wspd', 'wdirsin', 'wdircos']
        data = data[columns_to_keep]


        time.sleep(1)
        
        # data = data.dropna(axis=1, how='all')
        return data

    def export_hourly_data_to_csv(self):
        
        data_filename = f"{self.substation_name}_{self.start_date.year}{self.start_date.month}{self.start_date.day}"\
            f"_{self.end_date.year}{self.end_date.month}{self.end_date.day}"
        data_path =  f"{self.model_name}/{self.substation_name}"
    
        # create the directory_path folder if it doesn't exist
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
        if not any(data_filename in file_name for file_name in os.listdir(data_path)):
            df = self.get_hourly_data()
    
                
            # split the dataframe into new dataframes based on the DT column as the index
            dfs = {}
            for col in df.columns:
                
                file_path = os.path.join(data_path, f"{data_filename}_{col}.csv")
                dfs[col] = df[[col]]
                # dfs[col].to_csv(f"{self.substation_name}_{self.start_date.year}_{self.end_date.year}_{col}.csv")
                dfs[col].to_csv(file_path)
            self.data = dfs
        else:
            # Files containing data_filename exist, skip data processing
            print(f"WeatherData: Hourly data for these dates exist, skipping data processing")


    def clean_csv_file(self):
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(self.weather_file)

        # Convert the second column to a datetime object
        df.iloc[:, 1] = pd.to_datetime(df.iloc[:, 1])

        # Clean the 14th column and convert to a decimal number
        df.iloc[:, 13] = df.iloc[:, 13].str.replace('[^0-9.]', '').astype(float) / 100

        # Select the 2nd and 14th columns and add them to a new DataFrame
        new_df = pd.DataFrame({'DT': df.iloc[:, 1], 'temp': df.iloc[:, 13]})

        return new_df
    
    # Function to calculate Wet Bulb Temperature using Stull's formula
    def calculate_wet_bulb_temp(self, T, RH):
        T_w = T * math.atan(0.151977 * (RH + 8.313659)**0.5) + math.atan(T + RH) - math.atan(RH - 1.676331) + 0.00391838 * (RH)**1.5 * math.atan(0.023101 * RH) - 4.686035
        return T_w

    # Function to calculate Temperature-Humidity Index
    def calculate_thi(self, T, RH):
        THI = T - (0.55 - 0.0055 * RH) * (T - 14.5)
        return THI

    # Function to calculate Cooling Degree Hours
    def calculate_cdh(self, T, base_temp=18.3):
        return max(T - base_temp, 0) * 24

    # Function to calculate Heating Degree Hours
    def calculate_hdh(self, T, base_temp=18.3):
        return max(base_temp - T, 0) * 24
