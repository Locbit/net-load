import pandas as pd
from datetime import datetime, timedelta

from netload.training_data import TrainingData

from netload.substation_model import SubstationModel

##### SETUP #####

uname = "nlf2023-brucite@forecastarbiter.com"
pwd = "9zmhDY7Qvcw@goK*TIhC"

# Get current datetime
current_datetime = datetime.now()

# Add 14 hours
updated_datetime = current_datetime + timedelta(hours=14+24)

# Round to the nearest day
rounded_datetime = updated_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

# Get the integer value of the day
day = rounded_datetime.date().day

prediction_start_date = datetime(2023, 6, day,8) # 1 AM oregon time
prediction_end_date = prediction_start_date + timedelta(hours=23)


substation_name = 'Amity'
model_name = 'Amity'

regressor_path = f"{model_name}/{substation_name}/regressor/{substation_name}_regressor.csv"
training_path = f"{model_name}/{substation_name}/{substation_name}_training.csv"


uname = "nlf2023-brucite@forecastarbiter.com"
pwd = "9zmhDY7Qvcw@goK*TIhC"

# Get current datetime
current_datetime = datetime.now()

# Add 14 hours
updated_datetime = current_datetime + timedelta(hours=14+24)

# Round to the nearest day
rounded_datetime = updated_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

# Get the integer value of the day
day = rounded_datetime.date().day

print("------- COMPUTING FORECASTS -------")

#### AMITY SUBSTATION #####

try: 

    print("------- AMITY FORECAST -------")
    
    # 10 AM OR = 10 AM PST DUE DATE

    prediction_start_date = datetime(2023, 6, day,8) # 1 AM oregon time
    prediction_end_date = prediction_start_date + timedelta(hours=23)
    
    # amity_model_fname = 'best_model_Amity_2023-6-8.csv'
    amity_model_fname = 'best_model_San_Antonio_2023-6-8.csv'
    
    amity_model_data = [
                    ('Amity', (45.11697099005726, -123.20202573006682), True),
                    # ('DaytonCutoffSolar', (45.168832884164075, -123.13668793938469), False),
                    # ('ValleyCreekSolar', (45.03245271909166, -123.09466606026315), False),
                    # ('ButlerSolar', (45.10106068680774, -123.41456045471486), False),
                    # ('MillCreekSolar', (45.088307785035745, -123.42307867208085), False),
                    # ('RedPrarieSolar', (45.08715641433478, -123.41655553988588), False),
    
                    # # for whatever reason this makes the whole thing explode
                    # ('GrandeRondeSolar', (45.06344507542511, -123.61084728279289), False),
    
                  ]
    
    
    amity = SubstationModel('Amity',
                                amity_model_data,
                                training_start_date = datetime(2022, 1, 1),
                                # training_start_date = datetime(2023, 1, 1) - timedelta(days=200),
                                training_end_date = datetime(2023, 6, 22),
                                prediction_start_date = prediction_start_date,
                                prediction_end_date = prediction_end_date,
                                site_id = '5ebb4527-edbd-11ed-bf8d-128dcacebd72',
                                forecast_id = "56178e67-0044-11ee-bbbf-aa678857fb1c",
                                arbiter_uname = uname,
                                arbiter_pwd = pwd,
                                model_fname = amity_model_fname,
                                # model_fname = 'default_train'
                                overwrite = True
                                )
except Exception as e:
    print(e)
    


