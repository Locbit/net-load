import pandas as pd
import os
from concurrent import futures

'''
TrainingData class:

This class takes the grid load data and the weather data, filters out all
data between the start date and end date. This filtering is mainly done 
because of the format of Ausgrid data, data for FY2022 actually contains data
between 5/2021 and 5/2022 and this doesn't line up with data from meteostat.
This causes problems during imputation.

After the files are loaded and filtered, they are imputed and saved to a csv file.

'''

class TrainingData:
    def __init__(self, substation_name, model_name, start_date, end_date):
        self.substation_name = substation_name
        
        self.model_name = model_name
        
        self.start_date = start_date
        self.end_date = end_date
        self.raw_data = []
        self.filtered_raw_data = []
        self.imputed_data = []
        
        
        self.trained_data_path = f"{self.model_name}/{self.substation_name}/{self.substation_name}_training.csv"
        
        
        self.load_raw_data()
        self.filter_raw_data()
        self.impute()

    
    def merge_data(self):
        # Merge the filtered dataframes based on the 'DT' column
        merged_df = pd.merge(self.load_data_filtered, self.weather_data_filtered, on='DT')
        return merged_df
    

    def load_raw_data(self):
        # set the directory where your CSV files are located
        csv_directory =  f"{self.model_name}/{self.substation_name}"
        
        # create an empty list to store the dataframes
        df_list = []
        
        # loop through each file in the directory
        for filename in os.listdir(csv_directory):
            if filename.endswith('.csv') and not filename.endswith('_all_load.csv')\
            and not filename.endswith('_training.csv') :  # make sure the file is a CSV
                # read the CSV into a dataframe and append it to the list
                df_list.append(pd.read_csv(os.path.join(csv_directory, filename), index_col='DT', parse_dates=True))
        
        # print the list of dataframes
        self.raw_data = df_list
        
        
    def filter_raw_data(self):
        for df in self.raw_data:
            
            # Filter load_data by date range
            df = df[(df.index >= self.start_date) & (df.index <= self.end_date)]
            
            self.filtered_raw_data.append(df)
        
    def resample_data(self, df, interval):
        
        # print(df)
        return df.resample(interval).interpolate()
    
    def process_dataframes(self, df_list, resample_interval='1h'):
        dataframes = df_list
    
        with futures.ThreadPoolExecutor() as executor:
            # Resample the data concurrently
            future_to_resampled = {executor.submit(self.resample_data, df, resample_interval): df for df in dataframes}
            resampled_data = [future.result() for future in futures.as_completed(future_to_resampled)]
    
        # Merge the resampled data
        merged_data = pd.concat(resampled_data, axis=1).dropna()
        return merged_data

    def impute(self):

        df_list = self.filtered_raw_data
        resample_interval = '1h'  # Resample to a fixed 1-hour interval
        merged_data = self.process_dataframes(df_list, resample_interval)
        merged_data.to_csv(self.trained_data_path)
        
        self.imputed_data = merged_data
