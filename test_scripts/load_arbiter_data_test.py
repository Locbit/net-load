import pandas as pd

from netload.arbiter_substation_node import ArbiterSubstationNode
from netload.arbiter_load_data import ArbiterLoadData
from datetime import datetime, timedelta


substation_name = 'Waianae'

model_name = 'model1'

file_path = 'arbiter_data'

start_date = datetime(2023, 1, 28)
end_date = datetime(2023, 5, 31)


arbiter_data = ArbiterLoadData(substation_name, model_name, file_path, start_date, end_date)

