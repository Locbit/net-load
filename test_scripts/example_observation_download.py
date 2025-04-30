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

# get a list of the Observations your user has access to
observations = session.list_observations()
print("# of Observations:", len(observations))
#for observation in observations:
#    print(observation.name, observation.site.name)

# get info about a specific Observation (using its UUID)
obs = session.get_observation("540e3ddd-edc0-11ed-b470-128dcacebd72")
print(obs)
#print(obs.name)            # the name of the Observation
#print(obs.site.name)       # the name of the Site that the Observation is associated with
#print(obs.observation_id)  # the UUID of the Observation

# check the timerange of available data for a specific Observation
(start, end) = session.get_observation_time_range("540e3ddd-edc0-11ed-b470-128dcacebd72")
print("Start of data:", start)
print("End of data:", end)

# get data from a specific Observation
df = session.get_observation_values(
    "540e3ddd-edc0-11ed-b470-128dcacebd72",
    pd.Timestamp("2022-05-01 00:00:00Z"),  # May 1, 2022 at midnight (00 UTC)
    pd.Timestamp("2022-05-05 00:00:00Z"),  # May 3, 2022 at midnight (00 UTC)
)
print(df.head())
