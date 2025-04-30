from datetime import datetime
from meteostat import Hourly
from meteostat import Point
import pandas as pd
import pytz
import os
from concurrent import futures
import numpy as np

'''
PredictionData class:

'''

class PredictionData:
    def __init__(self, substation_name, model_name, start_date, end_date, location):
        self.substation_name = substation_name

        self.location = location
        
        self.start_date = start_date
        self.end_date = end_date
        
        self.weather_prediction_data = pd.DataFrame()
        self.load_prediction_data = pd.DataFrame()
        
        self.prediction_data = pd.DataFrame()
        
        self.load_file_path = f"{self.model_name}\{self.substation_name}\{self.substation_name}_all_load.csv"
        
        self.prediction_data_path = f"{self.model_name}\{self.substation_name}\{self.substation_name}_for_prediction.csv"
        
        self.substation_name = substation_name
        
        self.data = pd.DataFrame()
        
        self.prediction_array = []
        
        # get this data and put it to a csv
        self.get_weather_data()
        self.get_load_data()
        self.impute()
        self.prepare_data()
        

    def get_weather_data(self):

        data = Hourly(self.location, self.start_date, self.end_date).fetch()
        data = data.drop(columns=['coco', 'tsun', 'snow', 'wpgt'])
        
        
        data = data.rename_axis('DT')
        
        data = data.dropna(how='all')
        
        # the precipitation data column is articularly problematic as most of the data
        # is nans, which screws up the imputation process. if you fill those nans with
        # zeros, imputation works properly. this is a problem specific to datasets
        # which contain mostly nans.
        data['prcp'] = data['prcp'].fillna(0)
        
        # data = data.dropna(axis=1, how='all')
        
        self.weather_prediction_data = data
        

    # def export_hourly_data_to_csv(self):
        
    #     data_filename = f"{self.substation_name}_{self.start_date.year}{self.start_date.month}{self.start_date.day}"\
    #         f"_{self.end_date.year}{self.end_date.month}{self.end_date.day}"
    #     data_path = self.substation_name
        
    #     if not any(data_filename in file_name for file_name in os.listdir(data_path)):
    #         df = self.get_weather_data()
    
    #         # create the directory_path folder if it doesn't exist
    #         if not os.path.exists(self.substation_name):
    #             os.makedirs(self.substation_name)
                
    #         # split the dataframe into new dataframes based on the DT column as the index
    #         dfs = {}
    #         for col in df.columns:
    #             file_path = os.path.join(self.substation_name, f"{data_filename}_{col}_for_prediction.csv")
    #             dfs[col] = df[[col]]
    #             # dfs[col].to_csv(f"{self.substation_name}_{self.start_date.year}_{self.end_date.year}_{col}.csv")
    #             dfs[col].to_csv(file_path)
    #         self.weather_prediction_data = dfs
    #     else:
    #         # Files containing data_filename exist, skip data processing
    #         print(f"WeatherData: Hourly data for these dates exist, skipping data processing")


    # def clean_csv_file(self):
    #     # Load the CSV file into a pandas DataFrame
    #     df = pd.read_csv(self.weather_file)

    #     # Convert the second column to a datetime object
    #     df.iloc[:, 1] = pd.to_datetime(df.iloc[:, 1])

    #     # Clean the 14th column and convert to a decimal number
    #     df.iloc[:, 13] = df.iloc[:, 13].str.replace('[^0-9.]', '').astype(float) / 100

    #     # Select the 2nd and 14th columns and add them to a new DataFrame
    #     new_df = pd.DataFrame({'DT': df.iloc[:, 1], 'temp': df.iloc[:, 13]})

    #     return new_df
    
    
    def get_load_data(self):
        
        
        # Load the dataframe from the CSV file
        df = pd.read_csv(self.load_file_path)
        
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

        self.load_prediction_data = filtered_df
        
        
    def merge_data(self):
        # Merge the filtered dataframes based on the 'DT' column
        merged_df = pd.merge(self.load_data_filtered, self.weather_data_filtered, on='DT')
        return merged_df
    

    # def load_raw_data(self):
    #     # set the directory where your CSV files are located
    #     csv_directory = self.substation_name
        
    #     # create an empty list to store the dataframes
    #     df_list = []
        
    #     # loop through each file in the directory
    #     for filename in os.listdir(csv_directory):
    #         if filename.endswith('.csv'):  # make sure the file is a CSV
    #             # read the CSV into a dataframe and append it to the list
    #             df_list.append(pd.read_csv(os.path.join(csv_directory, filename), index_col='DT', parse_dates=True))
        
        
    #     # print the list of dataframes
    #     self.raw_data = df_list
        
        
    # def filter_raw_data(self):
    #     for df in self.raw_data:
            
    #         # Filter load_data by date range
    #         df = df[(df.index >= self.start_date) & (df.index <= self.end_date)]
            
    #         self.filtered_raw_data.append(df)
        
    def resample_data(self, df, interval):
        
        
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
        # Assuming you already have two DataFrames named temperature_df and power_df
        # temperature_df = pd.read_csv('temperature.csv', index_col='DT', parse_dates=True)
        # power_df = pd.read_csv('power.csv', index_col='DT', parse_dates=True)
        # pressure_df = pd.read_csv('pressure.csv', index_col='DT', parse_dates=True)

        df_list = [self.load_prediction_data, self.weather_prediction_data]
        
        # df_list = self.filtered_raw_data
        
        resample_interval = '1h'  # Resample to a fixed 1-hour interval
        merged_data = self.process_dataframes(df_list, resample_interval)
        
        # merged_data.drop(self.substation_name)
        
        # print(merged_data)
        
        merged_data.to_csv(self.prediction_data_path)
        
        self.prediction_data = merged_data

    def prepare_data(self):
        
        dwdf = self.prediction_data
        station = self.substation_name
        
        aggdata = dwdf[['temp', 'rhum', 'dwpt', 'wspd']].copy()
        
        # lagged_columns = []
        
        # for col in aggdata.columns:
        #     for i in range(1, 25):
        #         lagged_columns.append(aggdata[col].shift(periods=i).rename(col+'_{:d}h'.format(i)))
        #     aggdata[col+'_diff'] = aggdata[col].diff()
        #     aggdata[col+'_week'] = aggdata[col].shift(periods=24*7)
        
        # aggdata = pd.concat([aggdata] + lagged_columns, axis=1)
        
        dayhour_ind = aggdata.index.hour
        hr_sin = pd.Series(np.sin(dayhour_ind*(2.*np.pi/24)), index=aggdata.index, name='hr_sin')
        hr_cos = pd.Series(np.cos(dayhour_ind*(2.*np.pi/24)), index=aggdata.index, name='hr_cos')
        
        weekday_ind = aggdata.index.weekday
        week_sin = pd.Series(np.sin(weekday_ind*(2.*np.pi/7)), index=aggdata.index, name='week_sin')
        week_cos = pd.Series(np.cos(weekday_ind*(2.*np.pi/7)), index=aggdata.index, name='week_cos')
        weekend = pd.Series(np.asarray([0 if ind <= 4 else 1 for ind in weekday_ind]), index=aggdata.index, name='weekend')
        
        month_ind = aggdata.index.month
        mnth_sin = pd.Series(np.sin((month_ind-1)*(2.*np.pi/12)), index=aggdata.index, name='mnth_sin')
        mnth_cos = pd.Series(np.cos((month_ind-1)*(2.*np.pi/12)), index=aggdata.index, name='mnth_cos')
        
        aggdata = pd.concat([aggdata, hr_sin, hr_cos, week_sin, week_cos, weekend, mnth_sin, mnth_cos], axis=1)
        
        aggdata.dropna(inplace=True)
        aggdata.head()
        # print(aggdata)
        features = [col for col in aggdata.columns if col != station]
        X_pred = aggdata[features].values
        # X_pred = aggdata
        # print(X_pred)
        
        self.prediction_array = X_pred
        