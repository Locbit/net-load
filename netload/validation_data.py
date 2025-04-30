from datetime import datetime
from meteostat import Hourly
from meteostat import Point
import pandas as pd
import pytz
import os
from concurrent import futures
import numpy as np

'''
ValidationData class:

'''

class ValidationData:
    def __init__(self, substation_name, model_name, start_date, end_date):
        
        
        self.substation_name = substation_name
        self.model_name = model_name
        self.start_date = start_date
        self.end_date = end_date

        self.load_data = pd.DataFrame()

        self.validation_data = pd.DataFrame()

        self.load_file_path = f"{self.model_name}\{self.substation_name}\{self.substation_name}_all_load.csv"
    
        self.forecast = pd.DataFrame()

        self.get_load_data()

    
    def get_load_data(self):
        
        # Load the dataframe from the CSV file
        df = pd.read_csv(self.load_file_path, parse_dates=True)

        # Convert the 'DT' column to a datetime object
        df['DT'] = pd.to_datetime(df['DT'])
        
        # Define the start and end dates of the range you're interested in
        start_date = pd.Timestamp(self.start_date)
        end_date = pd.Timestamp(self.end_date)
        
        # Filter the dataframe to only include rows with DT within the date range
        filtered_df = df.loc[(df['DT'] >= start_date) & (df['DT'] <= end_date)]
        
        # Drop any rows with missing values in either the 'DT' or 'load' columns
        filtered_df.dropna(subset=['DT', self.substation_name], inplace=True)
        
        # Save the filtered dataframe to a new CSV file
        # filtered_df.to_csv( f"{self.substation_name}\{self.substation_name}_data_for_pred.csv", index=False)
        
        filtered_df['DT'] = pd.to_datetime(df['DT'])
        filtered_df.set_index('DT', inplace=True)

        self.validation_data = filtered_df
        