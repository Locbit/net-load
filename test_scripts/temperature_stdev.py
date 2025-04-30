import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point as sPoint
from shapely.ops import unary_union
import random
from meteostat import Point, Daily, Hourly
from datetime import datetime

'''
this code gets temperature data in sydney. 10 GPS locations are sampled at random across
the city limits of sydney. The standard deviation and average temperature are obtained.
The idea is that standard deviation and average temperature could be time series data that could be
used in the ML model to improve accuracy.
'''


# Replace this with your Meteostat API key
meteostat_api_key = 'your_api_key'

# Define the start and end dates for historical weather data
start_date = datetime(2020, 12, 21)
end_date = datetime(2020, 12, 31)

def random_points_within(poly, num_points):
    min_x, min_y, max_x, max_y = poly.bounds
    points = []

    while len(points) < num_points:
        random_point = sPoint([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if random_point.within(poly):
            points.append(random_point)

    return points

# Download the city boundary from OpenStreetMap
sydney_boundary_polygon = ox.geocode_to_gdf("Sydney, Australia").iloc[0]['geometry']

# Generate random points within the city boundary
num_points = 10
random_points = random_points_within(sydney_boundary_polygon, num_points)

# Convert the points to a DataFrame
coordinates = {'latitude': [point.y for point in random_points], 'longitude': [point.x for point in random_points]}
df = pd.DataFrame(coordinates)

print("Random GPS locations:")
print(df)

# Fetch historical weather data for the random locations
weather_data = []

for index, row in df.iterrows():
    location = Point(row['latitude'], row['longitude'])
    weather = Hourly(location, start_date, end_date)
    wd = weather.fetch()
    wd['location'] = index + 1
    
    if len(wd) > 0:
        weather_data.append(wd)

# Merge weather data from all locations
merged_weather_data = pd.concat(weather_data)

# Calculate the standard deviation and mean of tmax for each day
tmax_stats = merged_weather_data.groupby('time')['temp'].agg(['std', 'mean']).reset_index()

# Calculate the ratio of standard deviation to mean for each day
tmax_stats['ratio'] = tmax_stats['std'] / tmax_stats['mean']

# Create a new DataFrame with the results
tmax_ratio_df = tmax_stats[['time', 'ratio']]

print("\nRatio of standard deviation to mean of tmax for each day:")
print(tmax_ratio_df)
