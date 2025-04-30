import pandas as pd
from properscoring import crps_ensemble
import numpy as np

import matplotlib.pyplot as plt


# Read the data
df_forecast = pd.read_csv('prob_forecast_Waianae_2023-6-12.csv')
df_actual = pd.read_csv('actuals_Waianae_2023-6-12.csv')

# Convert timestamp to datetime
df_forecast['timestamp'] = pd.to_datetime(df_forecast['timestamp'])
df_actual['timestamp'] = pd.to_datetime(df_actual['timestamp'])


# We first need to align the actuals and forecast dataframes
df_combined = df_forecast.merge(df_actual, on='timestamp', how='inner')

# Initialize an empty list to hold the crps scores
crps_scores = []
# Loop through each row in the dataframe

for idx, row in df_combined.iterrows():
    # Extract the forecast probabilities and actual value
    forecast_probabilities = row[['p0', 'p10', 'p20', 'p30', 'p40', 'p50', 'p60', 'p70', 'p80', 'p90', 'p100']].values.astype(np.float64)
    actual_value = row['actual']

    # Make actual_value a 1-D array and forecast_probabilities a 2-D array
    actual_value_1d = np.array([actual_value]).astype(np.float64)  # make it a 1-D array
    forecast_probabilities_2d = forecast_probabilities.reshape(1, -1)  # make it a 2-D array

    # Calculate the CRPS for this row and append to list
    crps = crps_ensemble(actual_value_1d, forecast_probabilities_2d)
    crps_scores.append(crps)

# Convert the list of CRPS scores to a numpy array
crps_scores = np.array(crps_scores)

# Now you can compute summary statistics of the CRPS scores
print('CRPS mean: ', np.mean(crps_scores))
print('CRPS std: ', np.std(crps_scores))

plt.plot(crps_scores)