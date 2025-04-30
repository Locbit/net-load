# Import Meteostat library and dependencies
from datetime import datetime
from meteostat import Hourly
from meteostat import Point
import pandas as pd
from noaa_sdk import NOAA



# # Create Point for Vancouver, BC
# location = Point(32.72049098182996, -117.16603827662068, 70)

# # Set time period
# start = datetime(2023, 3, 1)
# end = datetime(2023, 3, 25, 23, 59)

# # Get hourly data
# data = Hourly(location, start, end)
# data = data.fetch()

# # Print DataFrame
# print(data)



def getforecast_hum(zip):
    n = NOAA()
    res = n.get_forecasts(zip, 'US', type='forecastGridData')
    for i in res:
        print(i)
        
    
    data = res['relativeHumidity']['values']
    
    df = pd.DataFrame(data)
    df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
    df['time'] = pd.to_datetime(df.time)
    df = df[['time', 'value']]
    df = df.rename(columns={'value': 'rhum'})

    return df


def getforecast_temp(zip):
    n = NOAA()
    res = n.get_forecasts(zip, 'US', type='forecastGridData')
    for i in res:
        print(i)
        
    
    data = res['temperature']['values']
    
    df = pd.DataFrame(data)
    df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
    df['time'] = pd.to_datetime(df.time)
    df = df[['time', 'value']]
    df = df.rename(columns={'value': 'temp'})

    return df


def getforecast_dewpoint(zip):
    n = NOAA()
    res = n.get_forecasts(zip, 'US', type='forecastGridData')
    
    # data_temp = res['temperature']['values']
    # df_temp = pd.DataFrame(data_temp)
    # df_temp[['time', 'validTime_duration']] = df_temp.validTime.str.split('/', expand=True)
    # df_temp['time'] = pd.to_datetime(df_temp.time)
    # df_temp = df_temp[['time', 'value']]
    # df_temp = df_temp.rename(columns={'value': 'temp'})
    
    data_dewpoint = res['dewpoint']['values']
    df_dewpoint = pd.DataFrame(data_dewpoint)
    df_dewpoint[['time', 'validTime_duration']] = df_dewpoint.validTime.str.split('/', expand=True)
    df_dewpoint['time'] = pd.to_datetime(df_dewpoint.time)
    df_dewpoint = df_dewpoint[['time', 'value']]
    df_dewpoint = df_dewpoint.rename(columns={'value': 'dwpt'})
    
    # df = pd.merge(df_temp, df_dewpoint, on='time')
    return df_dewpoint

def getforecast_wspd(zip):
    n = NOAA()
    res = n.get_forecasts(zip, 'US', type='forecastGridData')
    for i in res:
        print(i)
        
    
    data = res['transportWindSpeed']['values']
    
    df = pd.DataFrame(data)
    df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
    df['time'] = pd.to_datetime(df.time)
    df = df[['time', 'value']]
    df = df.rename(columns={'value': 'wspd'})

    return df

def getforecast_wdir(zip):
    # n = NOAA()
    # res = n.get_forecasts(zip, 'US', type='forecastGridData')
    # for i in res:
    #     print(i)
    
    n = NOAA()
    res = n.points_forecast(45.10106068680774, -123.41456045471486, type='forecastGridData')
    for i in res:
        print(i)
        
    print(res)
    data = res['transportWindDirection']['values']
    
    df = pd.DataFrame(data)
    df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
    df['time'] = pd.to_datetime(df.time)
    df = df[['time', 'value']]
    df = df.rename(columns={'value': 'wdir'})

    return df

def getforecast_prcp(zip):
    # n = NOAA()
    # res = n.get_forecasts(zip, 'US', type='forecastGridData')
    # for i in res:
    #     print(i)
    
    n = NOAA()
    res = n.points_forecast(45.10106068680774, -123.41456045471486, type='forecastGridData')
    for i in res:
        print(i)
    
    data = res['quantitativePrecipitation']['values']
    
    df = pd.DataFrame(data)
    df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
    df['time'] = pd.to_datetime(df.time)
    df = df[['time', 'value']]
    df = df.rename(columns={'value': 'prcp'})

    return df


n = NOAA()
res = n.points_forecast(45.10106068680774, -123.41456045471486, type='forecastGridData')
for i in res:
    print(i)
    
print(res)
data = res['transportWindDirection']['values']

df = pd.DataFrame(data)
df[['time', 'validTime_duration']] = df.validTime.str.split('/', expand=True)
df['time'] = pd.to_datetime(df.time)
df = df[['time', 'value']]
df = df.rename(columns={'value': 'wdir'})

    
# lol = getforecast_wdir(92107)
# print(lol)

# n = NOAA()
# res = n.get_forecasts(92107, 'US', type='forecastGridData')
