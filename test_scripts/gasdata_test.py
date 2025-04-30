from datetime import datetime, timedelta

from netload.substation_model import SubstationModel
from netload.gas_data import GasData

import matplotlib.pyplot as plt

import pytz

substation_name = 'gas_test'
model_name = 'gas_test'

start_date = datetime(2022, 5, 22, 23)
end_date = datetime(2023, 5, 29, 23)

# start_date = pytz.utc.localize(start_date)
# end_date = pytz.utc.localize(end_date)

gasdata = GasData(substation_name, model_name, start_date, end_date, ticker = 'NG=F')