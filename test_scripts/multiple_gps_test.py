from datetime import datetime, timedelta

from netload.substation_model import SubstationModel

import matplotlib.pyplot as plt

plt.close('all')


uname = "nlf2023-brucite@forecastarbiter.com"
pwd = "9zmhDY7Qvcw@goK*TIhC"


day = 11

prediction_start_date = datetime(2023, 6, day,11) # 1 AM Hawaii
prediction_end_date = prediction_start_date + timedelta(hours=23)

waianae_model_fname = 'best_model_Waianae_2023-6-8.csv'

waianae = SubstationModel('Waianae',
                            [('Waianae', (21.442829733191395, -158.1853281893482)),
                             ('Waianae', (21.442829733191395, -158.1853281893482))],
                            training_start_date = datetime(2022, 5, 31),
                            training_end_date = datetime(2023, 5, 31),
                            prediction_start_date = prediction_start_date,
                            prediction_end_date = prediction_end_date,
                            # site_id = '5ebb4527-edbd-11ed-bf8d-128dcacebd72' ,
                            site_id = 'c639b1f3-eb8f-11ed-802e-aec5a60999dc',
                            # forecast_id = "56178e67-0044-11ee-bbbf-aa678857fb1c",
                            forecast_id = '5d2d9c84-0044-11ee-acf5-22bbbfba48a8',
                            arbiter_uname = uname,
                            arbiter_pwd = pwd,
                            model_fname = waianae_model_fname
                            )

waianae.forecast_node_for_arbiter('Waianae')