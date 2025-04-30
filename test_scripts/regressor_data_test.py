# Import Meteostat library and dependencies
from datetime import datetime, timedelta
from meteostat import Hourly
from meteostat import Point
import pandas as pd
from noaa_sdk import NOAA
import os
from concurrent import futures


    
def getforecast_hum(lat, lon):
    n = NOAA()
    res = n.points_forecast(lat, lon, type='forecastGridData')
    for i in res:
        print(i)
        
    
    data = res['properties']['relativeHumidity']['values']
    
    df = pd.DataFrame(data)
    df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
    df['time'] = pd.to_datetime(df.time)
    df = df[['time', 'value']]
    df = df.rename(columns={'value': 'rhum'})

    return df


def getforecast_temp(lat, lon):
    n = NOAA()
    res = n.points_forecast(lat, lon, type='forecastGridData')
    for i in res:
        print(i)
    
    data = res['properties']['temperature']['values']
    
    df = pd.DataFrame(data)
    df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
    df['time'] = pd.to_datetime(df.time)
    df = df[['time', 'value']]
    df = df.rename(columns={'value': 'temp'})

    return df


def getforecast_dewpoint(lat, lon):
    n = NOAA()
    res = n.points_forecast(lat, lon, type='forecastGridData')
    
    data_dewpoint = res['properties']['dewpoint']['values']
    df_dewpoint = pd.DataFrame(data_dewpoint)
    df_dewpoint[['time', 'validTime_duration']] = df_dewpoint.validTime.str.split('/', expand=True)
    df_dewpoint['time'] = pd.to_datetime(df_dewpoint.time)
    df_dewpoint = df_dewpoint[['time', 'value']]
    df_dewpoint = df_dewpoint.rename(columns={'value': 'dwpt'})
    
    # df = pd.merge(df_temp, df_dewpoint, on='time')
    return df_dewpoint


# def resample_data(df, interval):
    
#     # print(df)
#     return df.resample(interval).interpolate()

# def process_dataframes(df_list, resample_interval='1h'):
#     dataframes = df_list

#     with futures.ThreadPoolExecutor() as executor:
#         # Resample the data concurrently
#         future_to_resampled = {executor.submit(self.resample_data, df, resample_interval): df for df in dataframes}
#         resampled_data = [future.result() for future in futures.as_completed(future_to_resampled)]

#     # Merge the resampled data
#     merged_data = pd.concat(resampled_data, axis=1).dropna()
#     return merged_data

# def impute():

#     df_list = self.filtered_raw_data
#     resample_interval = '1h'  # Resample to a fixed 1-hour interval
#     merged_data = self.process_dataframes(df_list, resample_interval)
#     merged_data.to_csv(self.trained_data_path)
    
#     self.imputed_data = merged_data
    
def filter_data(df, start_date, end_date):
    
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

    
# # Create Point for hawaii
lat = 21.442829733191395
lon = -158.1853281893482

# Get current datetime
current_datetime = datetime.now()

# Add 14 hours
updated_datetime = current_datetime + timedelta(hours=14+24)

# Round to the nearest day
rounded_datetime = updated_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

# Get the integer value of the day
day = rounded_datetime.date().day


prediction_start_date = datetime(2023, 6, day,11) # 1 AM Hawaii
prediction_end_date = prediction_start_date + timedelta(hours=23)


temp_df = getforecast_temp(lat, lon)
hum_df = getforecast_hum(lat, lon)   
dew_df = getforecast_dewpoint(lat, lon)

# Write temp_df to CSV
temp_df.to_csv('temp.csv', index=False)

# Write hum_df to CSV
hum_df.to_csv('humidity.csv', index=False)

# Write dew_df to CSV
dew_df.to_csv('dewpoint.csv', index=False)

file_paths = ['temp.csv', 'humidity.csv', 'dewpoint.csv']
resample_interval = '1h'  # Resample to a fixed 1-minute interval

with futures.ThreadPoolExecutor() as executor:
    # Read and resample the data concurrently
    future_to_resampled = {executor.submit(read_csv, file_path): file_path for file_path in file_paths}
    resampled_data = [future.result().pipe(resample_data, resample_interval) for future in futures.as_completed(future_to_resampled)]

# Merge the resampled data
merged_data = pd.concat(resampled_data, axis=1).dropna()
merged_data.to_csv('imputed.csv')

filtered_data = filter_data(merged_data, prediction_start_date, prediction_end_date)

filtered_data.to_csv('regressor_data.csv')



