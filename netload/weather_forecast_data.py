
# Import Meteostat library and dependencies
from datetime import datetime, timedelta
from meteostat import Hourly
from meteostat import Point
import pandas as pd
import numpy as np
import math
from noaa_sdk import NOAA
import os
from concurrent import futures
from netload.imputer import Imputer

class WeatherForecastData:
    def __init__(self, substation_name, model_name, substation_loc, start_date, end_date):
        self.substation_name = substation_name
        

        self.location = Point(substation_loc[0], substation_loc[1])
        
        self.lat = substation_loc[0]
        self.lon = substation_loc[1]
        
        
        self.start_date = start_date
        self.end_date = end_date
        
        
        self.data = pd.DataFrame()
        
        self.model_name = model_name
        

        self.start_date = start_date
        self.end_date = end_date
        
        self.raw_data = []
        
        self.imputed_data = None
        
        self.filtered_imputed_data = []
        
        self.weather_forecast_data_path =  f"{self.model_name}/{self.substation_name}/weather_forecast"
        self.imputed_data_path =  f"{self.model_name}/{self.substation_name}/weather_forecast"
        
        self.get_data_for_weather_forecast(self.lat, self.lon)

        
        imputer = Imputer(self.raw_data, resample_interval = '1h')
        self.imputed_data = imputer.process_dataframes()
    
    
        self.calc_weather_metrics()
        
        
        # Create the "weather_forecast" directory if it doesn't exist
        directory = self.weather_forecast_data_path
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        self.filtered_imputed_data = self.filter_imputed_data(self.imputed_data, start_date, end_date)

        self.filtered_imputed_data.to_csv(os.path.join(directory, f"{self.substation_name}_weather_forecast.csv"), index=True)

        


    def get_data_for_weather_forecast(self, lat, lon):
        temp_df = self.getforecast_temp(lat, lon)
        hum_df = self.getforecast_hum(lat, lon)
        dew_df = self.getforecast_dewpoint(lat, lon)

        wdir_df = self.getforecast_wdir(lat, lon)
        wspd_df = self.getforecast_wspd(lat, lon)
        prcp_df = self.getforecast_prcp(lat, lon)
        
        # Create the "weather_forecast" directory if it doesn't exist
        directory = self.weather_forecast_data_path
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write temp_df to CSV in the "weather_forecast" directory
        temp_df.to_csv(os.path.join(directory, f"{self.substation_name}_reg_temp_raw.csv"), index=False)
        
        # Write hum_df to CSV in the "weather_forecast" directory
        hum_df.to_csv(os.path.join(directory, f"{self.substation_name}_reg_hum_raw.csv"), index=False)
        
        # Write dew_df to CSV in the "weather_forecast" directory
        dew_df.to_csv(os.path.join(directory, f"{self.substation_name}_reg_dew_raw.csv"), index=False)

        
        wspd_df.to_csv(os.path.join(directory, f"{self.substation_name}_reg_wspd_raw.csv"), index=False)
        
        wdir_df.to_csv(os.path.join(directory, f"{self.substation_name}_reg_wdir_raw.csv"), index=False)
        
        prcp_df.to_csv(os.path.join(directory, f"{self.substation_name}_reg_prcp_raw.csv"), index=False)
        
        # create an empty list to store the dataframes
        df_list = []
        
        # loop through each file in the directory
        for filename in os.listdir(directory):
            if filename.endswith('raw.csv'):
                # read the CSV into a dataframe and append it to the list
                df_list.append(pd.read_csv(os.path.join(directory, filename), index_col='DT', parse_dates=True))
        
        # print the list of dataframes
        self.raw_data = df_list
        

        

    def getforecast_hum(self, lat, lon):
        n = NOAA()
        res = n.points_forecast(lat, lon, type='forecastGridData')
        # for i in res:
        #     print(i)
            
        
        data = res['properties']['relativeHumidity']['values']
        
        df = pd.DataFrame(data)
        df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
        df['time'] = pd.to_datetime(df.time)
        df = df[['time', 'value']]
        df = df.rename(columns={'time': 'DT', 'value': 'rhum'})
        # df = df.set_index('DT')
        
        # df.index = pd.to_datetime(df.index, utc = True)
    
        return df
    
    
    def getforecast_temp(self, lat, lon):
        n = NOAA()
        res = n.points_forecast(lat, lon, type='forecastGridData')
        # for i in res:
        #     print(i)
        
        data = res['properties']['temperature']['values']
        
        df = pd.DataFrame(data)
        df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
        df['time'] = pd.to_datetime(df.time)
        df = df[['time', 'value']]
        df = df.rename(columns={'time': 'DT', 'value': 'temp'})
        # df = df.set_index('DT')

        # df.index = pd.to_datetime(df.index, utc = True)

    
        return df
    
    
    def getforecast_dewpoint(self, lat, lon):
        n = NOAA()
        res = n.points_forecast(lat, lon, type='forecastGridData')
        
        data_dewpoint = res['properties']['dewpoint']['values']
        df_dewpoint = pd.DataFrame(data_dewpoint)
        df_dewpoint[['time', 'validTime_duration']] = df_dewpoint.validTime.str.split('/', expand=True)
        df_dewpoint['time'] = pd.to_datetime(df_dewpoint.time)
        df_dewpoint = df_dewpoint[['time', 'value']]
        df_dewpoint = df_dewpoint.rename(columns={'time': 'DT', 'value': 'dwpt'})
        # df_dewpoint = df_dewpoint.set_index('DT')

        # df_dewpoint.index = pd.to_datetime(df_dewpoint.index, utc = True)


        # df = pd.merge(df_temp, df_dewpoint, on='time')
        return df_dewpoint
    

    def getforecast_wspd(self, lat, lon):
        n = NOAA()
        res = n.points_forecast(lat, lon, type='forecastGridData')
        # for i in res:
        #     print(i)
            
        
        data = res['properties']['transportWindSpeed']['values']

        df = pd.DataFrame(data)
        df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
        df['time'] = pd.to_datetime(df.time)
        df = df[['time', 'value']]
        df = df.rename(columns={'time': 'DT', 'value': 'wspd'})
    
        return df
    
    def getforecast_wdir(self, lat, lon):
        n = NOAA()
        res = n.points_forecast(lat, lon, type='forecastGridData')
        # for i in res:
        #     print(i)
            
        
        data = res['properties']['transportWindDirection']['values']
        
        df = pd.DataFrame(data)
        df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
        df['time'] = pd.to_datetime(df.time)
        df = df[['time', 'value']]
        df = df.rename(columns={'time': 'DT', 'value': 'wdir'})
    
        return df
    
    def getforecast_prcp(self, lat, lon):
        n = NOAA()
        res = n.points_forecast(lat, lon, type='forecastGridData')
        # for i in res:
        #     print(i)
            
        data = res['properties']['quantitativePrecipitation']['values']
        

        
        df = pd.DataFrame(data)
        df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
        df['time'] = pd.to_datetime(df.time)
        df = df[['time', 'value']]
        df = df.rename(columns={'time': 'DT', 'value': 'prcp'})
    
        return df
    
    
    def calc_weather_metrics(self):
        
        data = self.imputed_data
        
        print(data)
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
        self.imputed_data = data[columns_to_keep]
        
        print(self.imputed_data)
        
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

        
    def filter_imputed_data(self, df, start_date, end_date):
        
        filtered_data = pd.DataFrame()
        
    
        # Convert start_date and end_date to the appropriate data type
        start_date = pd.to_datetime(start_date, utc=True)
        end_date = pd.to_datetime(end_date, utc=True)
    
        
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        filtered_data = df
        
        return filtered_data

    
    def read_csv(file_path):
        return pd.read_csv(file_path, index_col='time', parse_dates=True)
    
    def resample_data(df, interval):
        return df.resample(interval).interpolate()

    