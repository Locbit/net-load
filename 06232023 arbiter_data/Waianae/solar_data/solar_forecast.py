import pandas as pd
# from auto_ts import auto_timeseries
from autots import AutoTS, load_hourly
from autots import tools

import datetime as dt

import matplotlib.pyplot as plt

import numpy as np

plt.close('all')

# Load the data into a DataFrame
data = pd.read_csv("Waianae_solar_imputed.csv")

# Convert the 'datetime' column to datetime format
data['DT'] = pd.to_datetime(data['DT'])

prediction_start_date = pd.to_datetime(data['DT'].max())

prediction_end_date = dt.datetime(2023, 5, 31)

# Calculate the time difference
time_difference = prediction_end_date - prediction_start_date

# Extract the number of hours
hours = int(time_difference.total_seconds() / 3600)

# Set the 'datetime' column as the index
data.set_index('DT', inplace=True)
# also load: _hourly, _monthly, _weekly, _yearly, or _live_daily

# sample datasets can be used in either of the long or wide import shapes
long = False
# df = data(long=long)
df = data

model = AutoTS(
    forecast_length=hours,
    frequency='infer',
    prediction_interval=0.9,
    ensemble=None,
    model_list="superfast",  # "superfast", "default", "fast_parallel"
    transformer_list="superfast",  # "superfast",
    drop_most_recent=1,
    max_generations=4,
    num_validations=2,
    validation_method="backwards"
)
model = model.fit(
    df,
    date_col='datetime' if long else None,
    value_col='value' if long else None,
    id_col='series_id' if long else None,
)

prediction = model.predict()

forecast_df = prediction.forecast

forecast_df = forecast_df.drop(forecast_df.index[-1])

forecast_df.to_csv('Waianae_solar_forecast.csv')

combined_df = pd.concat([df, forecast_df])

combined_df.to_csv('Waianae_solar.csv')

# # Initialize an empty DataFrame
# new_df = pd.DataFrame()

# node_name = 'Waianae'

# Loop over each entry in the dictionary
# for key, predictionObject in prediction.items():
#     # Extract the 'load' column from the forecast DataFrame
    

#     load_series = predictionObject.upper_forecast[node_name]
    
#     new_key = f"p{int(float(key)*100)}"
    
#     # Add the series to the new DataFrame, renaming it according to the dictionary key
#     new_df[node_name + '_' + new_key] = load_series
    
    
# new_df.to_csv('Waianae_solar.csv')

# plt.plot(new_df)
# plt.plot(prediction['0'].forecast[node_name], marker='x', label='forecast')
# plt.show()

# plt.figure()
# # plt.plot(new_df2)
# plt.plot(prediction['0'].forecast[node_name], marker='o', label='forecast')
# plt.plot(prediction['0.5'].forecast[node_name], marker='x', label='forecast')
# plt.show()

# # plot a sample
# # prediction.plot(model.df_wide_numeric,
# #                 series=model.df_wide_numeric.columns[6],
# #                 start_date="2020-01-01")
# # Print the details of the best model
# print(model)

# # point forecasts dataframe
# forecasts_df = prediction.forecast
# # upper and lower forecasts
# forecasts_up, forecasts_low = prediction.upper_forecast, prediction.lower_forecast

# # accuracy of all tried model results
# model_results = model.results()
# # and aggregated from cross validation
# validation_results = model.results("validation")



# # lol = tools.probabilistic.inferred_normal(model.df_wide_numeric, forecasts_df, prediction_interval = 0.1)
# # lol2 = tools.probabilistic.inferred_normal(model.df_wide_numeric, forecasts_df, prediction_interval = 0.9)

# lol = tools.probabilistic.Point_to_Probability(model.df_wide_numeric,
#                                                forecasts_df,
#                                                prediction_interval = 0.7,
#                                                method = 'historic_quantile')

# lol2 = tools.probabilistic.Point_to_Probability(model.df_wide_numeric,
#                                                forecasts_df,
#                                                prediction_interval = 0.3,
#                                                method = 'historic_quantile')



# plt.plot(lol[1]['temp'], label='infer_lo')
# plt.plot(lol2[1]['temp'],label='infer_hi')
# plt.plot(forecasts_df['temp'], marker='x', label='forecast')
# plt.plot(forecasts_low['temp'], marker = 'o', color='blue', label='fore_lo')
# plt.plot(forecasts_up['temp'], marker = 'o', color='red', label='fore_hi')

# plt.legend()

# plt.show()

