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

'''get api token'''

token = api.request_cli_access_token(uname, pwd)

session = api.APISession(token, base_url="https://api.forecastarbiter.com")

''' list forecasts '''
forecasts = session.list_probabilistic_forecasts()


# List of forecast IDs to search for
forecast_ids = [
    "56178e67-0044-11ee-bbbf-aa678857fb1c", #amity
    "4647b078-0044-11ee-971c-22bbbfba48a8", # donalsonville
    "4ea42e3b-0044-11ee-ad98-22bbbfba48a8", #san antonio
    "5d2d9c84-0044-11ee-acf5-22bbbfba48a8" # forecast for waianae
                ]

# New list to store matching Forecast objects
matching_forecasts = []

# Loop through the forecasts list and filter based on forecast_id
for forecast in forecasts:
    print(forecast.forecast_id)
    if forecast.forecast_id in forecast_ids:
        matching_forecasts.append(forecast)

# Print the matching forecasts
for forecast in matching_forecasts:
    print(f"Matching forecast_id: {forecast.forecast_id}")
    print(f"lead time to start: {forecast.lead_time_to_start}")
