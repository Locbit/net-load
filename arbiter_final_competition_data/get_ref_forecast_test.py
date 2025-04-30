"""Example of download Observation data using the API."""

from solarforecastarbiter.io import api
import pandas as pd

# get a token from Auth0, where the token is used to authenticate all API
# requests instead of your username + password
#
# NOTE: each token has a 3-hour lifetime, which means you can cache the token
# but will need to get a fresh token after 3-hours

uname = "nlf2023-brucite@forecastarbiter.com"
pwd = "9zmhDY7Qvcw@goK*TIhC"

token = api.request_cli_access_token(uname, pwd)

# create session using the token, making sure to set the `base_url` to the new
# URL for the Arbiter's API
session = api.APISession(token, base_url="https://api.forecastarbiter.com")

# # get a list of the Observations your user has access to
# observations = session.list_observations()
# print("# of Observations:", len(observations))
# #for observation in observations:
# #    print(observation.name, observation.site.name)

# # get info about a specific Observation (using its UUID)
# obs = session.get_observation("540e3ddd-edc0-11ed-b470-128dcacebd72")
# print(obs)
# #print(obs.name)            # the name of the Observation
# #print(obs.site.name)       # the name of the Site that the Observation is associated with
# #print(obs.observation_id)  # the UUID of the Observation

# # check the timerange of available data for a specific Observation
# (start, end) = session.get_observation_time_range("540e3ddd-edc0-11ed-b470-128dcacebd72")
# print("Start of data:", start)
# print("End of data:", end)


'''
UUIDS:
    Amity:
        Probabilistic forecasts: 56178e67-0044-11ee-bbbf-aa678857fb1c
        Reference forecasts: 49cdf54e-0043-11ee-a581-aa678857fb1c
        Observations: 8db7d9ce-f3b2-11ed-a4f1-42ea8684a302

    Donalsonville:
        Probabilistic forecasts: 4647b078-0044-11ee-971c-22bbbfba48a8
        Reference forecasts: 3b6b45e3-0043-11ee-bfe9-aa678857fb1c
        Observations: 9e6d0bc3-f3b2-11ed-b529-42ea8684a302

    San Antonio:
        Probabilistic forecasts: 4ea42e3b-0044-11ee-ad98-22bbbfba48a8
        Reference forecasts: 496055a3-0043-11ee-ada4-aa678857fb1c
        Observations: 65e35193-f3b2-11ed-bec8-42ea8684a302
            
    Waianae:
        Probabilistic forecasts: 5d2d9c84-0044-11ee-acf5-22bbbfba48a8
        Reference forecasts: 4a3de81c-0043-11ee-a474-aa678857fb1c
        Observations: 540e3ddd-edc0-11ed-b470-128dcacebd72
            
'''

name = 'waianae'

uuid3 = '5d2d9c84-0044-11ee-acf5-22bbbfba48a8'
uuid2 = '4a3de81c-0043-11ee-a474-aa678857fb1c'
uuid1 = "540e3ddd-edc0-11ed-b470-128dcacebd72"


# get data from a locbits forecast
df3 = session.get_probabilistic_forecast_values(
    uuid3, #amity
    pd.Timestamp("2023-01-01 00:00:00Z"),  # May 1, 2022 at midnight (00 UTC)
    pd.Timestamp("2023-07-20 00:00:00Z"),  # May 3, 2022 at midnight (00 UTC)
)

df3.to_csv(f"{name}_forecasts.csv")

# get data from a specific reference forecast
df2 = session.get_probabilistic_forecast_values(
    uuid2, #amity
    pd.Timestamp("2023-01-01 00:00:00Z"),  # May 1, 2022 at midnight (00 UTC)
    pd.Timestamp("2023-07-20 00:00:00Z"),  # May 3, 2022 at midnight (00 UTC)
)

df2.to_csv(f"{name}_reference.csv")

# get data from a specific Observation
df = session.get_observation_values(
    uuid1,
    pd.Timestamp("2022-01-01 00:00:00Z"),  # May 1, 2022 at midnight (00 UTC)
    pd.Timestamp("2023-07-20 00:00:00Z"),  # May 3, 2022 at midnight (00 UTC)
)


df.to_csv(f"{name}_observation.csv")


