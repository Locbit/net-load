"""Example of interacting with ProbabilisticForecast data using the API."""

from solarforecastarbiter.io import api
import pandas as pd

# get a token from Auth0, where the token is used to authenticate all API
# requests instead of your username + password
#
# NOTE: each token has a 3-hour lifetime, which means you can cache the token
# but will need to get a fresh token after 3-hours
token = api.request_cli_access_token("<username>", "<password>")

# create session using the token, making sure to set the `base_url` to the new
# URL for the Arbiter's API
session = api.APISession(token, base_url="https://api.forecastarbiter.com")

# get a list of ProbabilisticForecasts your user has access to
forecasts = session.list_probabilistic_forecasts()
for forecast in forecasts:
    if forecast.provider == "2023 Net Load Forecasting Prize":
        print(forecast.name, forecast.site.name, forecast.forecast_id)

# get info about a specific ProbabilisticForecast (using its UUID)
forecast = session.get_probabilistic_forecast("4a3de81c-0043-11ee-a474-aa678857fb1c")
print(forecast)
#print(forecast.name)
#print(forecast.forecast_id)
#print(forecast.site.name)
#print(forecast.issue_time_of_day)
#print(forecast.variable)
#print(forecast.constant_values)

# get info about the ProbabilisticForecastConstantValues assocaited with the
# ProbabilisticForecast
# - ProbabilistcForecast = a collection of ProbabilisticForecastConstantValue objects
# - ProbabilisticForecastConstantValues = a forecast for a specific percentile
forecast = session.get_probabilistic_forecast("4a3de81c-0043-11ee-a474-aa678857fb1c")
for constant_value in forecast.constant_values:
    print(constant_value.constant_value, constant_value.constant_value_units, constant_value.forecast_id)

## submit data to a specific percentile of a probabilistic forecast for a site
#df = pd.read_csv("example_p50_forecast.csv", parse_dates=[0], index_col=0)["value"]
#session.post_probabilistic_forecast_constant_value_values(
#    "4a4f0a4d-0043-11ee-ab6c-aa678857fb1c",  # forecast_id
#    df                                       # pandas.Series
#)

# submit data for each percentile of a probabilistic forecast for a single site:
# 1. load data from a CSV file
# 2. for each percentile/probabilitiy: submit the forecast data
#
# Notes:
# - this example uses a CSV file that was already created, where the CSV has
#   all of the forecast probabilities as different columns (e.g., p50 = 50th
#   percentile)
# - the data in the CSV is fictional
# - this example hardcodes the UUIDs of each forecast percentile for a single
#   site and the corresponding column name in the CSV file
# - to use this example, you would need to update the UUIDs to those of your
#   team's specific forecast (e.g., if Team Diamond, use the UUIDs for the
#   "Diamond" forecasts)
#
#df = pd.read_csv("example_cdf_forecast.csv", parse_dates=[0], index_col=0)
#
#forecast_ids = [
#    # forecast UUID, column name in the CSV file
#    ["4a40f329-0043-11ee-9a8a-aa678857fb1c", "p0"],  # Prob(Net Load <= x) = 0%
#    ["4a43e86a-0043-11ee-8721-aa678857fb1c", "p10"], # Prob(Net Load <= x) = 10%
#    ["4a46d21d-0043-11ee-b169-aa678857fb1c", "p20"], # etc.
#    ["4a49be8e-0043-11ee-9fee-aa678857fb1c", "p30"],
#    ["4a4c5183-0043-11ee-8c6c-aa678857fb1c", "p40"],
#    ["4a4f0a4d-0043-11ee-ab6c-aa678857fb1c", "p50"],
#    ["4a514419-0043-11ee-bbfd-aa678857fb1c", "p60"],
#    ["4a53f7ef-0043-11ee-8399-aa678857fb1c", "p70"],
#    ["4a575fc9-0043-11ee-9c41-aa678857fb1c", "p80"],
#    ["4a59e05c-0043-11ee-8b19-aa678857fb1c", "p90"],
#    ["4a5c78ee-0043-11ee-b799-aa678857fb1c", "p100"],
#]
#
#for forecast_id, col in forecast_ids:
#    data = df[col]
#    session.post_probabilistic_forecast_constant_value_values(
#        forecast_id,
#        data,
#    )
