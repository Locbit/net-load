import pandas as pd
import numpy as np
import xarray as xr
from climpred import HindcastEnsemble

import numpy as np


# Adapted to numpy from pyro.ops.stats.crps_empirical
# Copyright (c) 2017-2019 Uber Technologies, Inc.
# SPDX-License-Identifier: Apache-2.0
def crps(y_true, y_pred, sample_weight=None):
    num_samples = y_pred.shape[0]
    absolute_error = np.mean(np.abs(y_pred - y_true), axis=0)

    if num_samples == 1:
        return np.average(absolute_error, weights=sample_weight)

    y_pred = np.sort(y_pred, axis=0)
    diff = y_pred[1:] - y_pred[:-1]
    weight = np.arange(1, num_samples) * np.arange(num_samples - 1, 0, -1)
    weight = np.expand_dims(weight, -1)

    per_obs_crps = absolute_error - np.sum(diff * weight, axis=0) / num_samples**2
    return np.average(per_obs_crps, weights=sample_weight)

def crps2(y_true, y_pred, sample_weight=None):
    y_true = np.expand_dims(y_true, -1)  # add an extra dimension to y_true
    num_samples = y_pred.shape[0]
    absolute_error = np.mean(np.abs(y_pred - y_true), axis=0)

    if num_samples == 1:
        return np.average(absolute_error, weights=sample_weight)

    y_pred = np.sort(y_pred, axis=0)
    diff = y_pred[1:] - y_pred[:-1]
    weight = np.arange(1, num_samples) * np.arange(num_samples - 1, 0, -1)
    weight = np.expand_dims(weight, -1)

    per_obs_crps = absolute_error - np.sum(diff * weight, axis=0) / num_samples**2
    return np.average(per_obs_crps, weights=sample_weight)



# Read the data
df_forecast = pd.read_csv('prob_forecast_Waianae_2023-6-12.csv')
df_actual = pd.read_csv('actuals_Waianae_2023-6-12.csv')

# Convert timestamp to datetime
df_forecast['timestamp'] = pd.to_datetime(df_forecast['timestamp'])
df_actual['timestamp'] = pd.to_datetime(df_actual['timestamp'])


# Assuming your DataFrame is called 'df'
columns_to_keep = ['p' + str(i) for i in range(0, 101, 10)]  # Generate column names p0 to p100
new_df = df_forecast[columns_to_keep]  # Select only the desired columns

# Convert the DataFrame to a NumPy array
forecast_arr = new_df.to_numpy()

actuals_arr = df_actual['actual'].to_numpy()

lol = crps2(actuals_arr, forecast_arr)

import matplotlib.pyplot as plt

# Plot the actual values
plt.plot(actuals_arr, label='Actuals')

# Plot the mean forecasted values
mean_forecast = np.mean(forecast_arr, axis=1)  # Calculate the mean across quantiles
plt.plot(mean_forecast, label='Forecasts')

plt.plot(forecast_arr, label='Prob Forecast')

plt.xlabel('Time')
plt.ylabel('Value')
plt.title('Actuals vs Forecasts')
plt.legend()

plt.show()
