import pandas as pd

from pytz import timezone

from solarforecastarbiter.io import api

from datetime import datetime, timedelta

uname = "nlf2023-brucite@forecastarbiter.com"
pwd = "9zmhDY7Qvcw@goK*TIhC"

# model_name ='Waianae'
# node_name = 'Waianae'
# site_id = 'c639b1f3-eb8f-11ed-802e-aec5a60999dc' # site id for waianae
# forecast_id = "5d2d9c84-0044-11ee-acf5-22bbbfba48a8" # forecast for waianae

# model_name ='Donalsonville'
# node_name = 'Donalsonville'
# site_id = '90c2a42c-f0ad-11ed-94b4-5edf5e2b3336'
# forecast_id = "4647b078-0044-11ee-971c-22bbbfba48a8"

# model_name ='Amity'
# node_name = 'Amity'
# site_id = '5ebb4527-edbd-11ed-bf8d-128dcacebd72' 
# forecast_id = "56178e67-0044-11ee-bbbf-aa678857fb1c"

model_name ='San_Antonio'
node_name = 'San_Antonio'
site_id = "8568f10f-eb8f-11ed-a556-128dcacebd72"
forecast_id = "4ea42e3b-0044-11ee-ad98-22bbbfba48a8"


prediction_date = datetime(2023, 6, 6)

data_filename = f"{model_name}/prob_forecast_{node_name}_{prediction_date.year}-{prediction_date.month}-{prediction_date.day}.csv"

df = pd.read_csv(data_filename)

'''get api token'''

token = api.request_cli_access_token(uname, pwd)

session = api.APISession(token, base_url="https://api.forecastarbiter.com")

arbiter_forecast = session.get_probabilistic_forecast(forecast_id)

forecast_ids = [item.forecast_id for item in arbiter_forecast.constant_values]

# '''prepare data'''

# ## read data

df.set_index(df.columns[0], inplace=True)

# Convert the datetime column to datetime
df.index = pd.to_datetime(df.index)

# '''upload data'''

for i, forecast_id in enumerate(forecast_ids):
    col = df.columns[i]  # Get the column name/index from the DataFrame
    forecast_series = df[col]
    print(f"{forecast_id}, {forecast_series}")
    session.post_probabilistic_forecast_constant_value_values(forecast_id, forecast_series)