from datetime import datetime, timedelta

from netload.substation_model import SubstationModel

import matplotlib.pyplot as plt

import pytz

plt.close('all')

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
month = rounded_datetime.date().month

print("------- COMPUTING FORECASTS -------")

#### AMITY SUBSTATION #####

# try: 
    
print("------- AMITY FORECAST -------")

# 10 AM OR = 10 AM PST DUE DATE

prediction_start_date = datetime(2023, month, day,8) # 1 AM oregon time
prediction_end_date = prediction_start_date + timedelta(hours=23)

# amity_model_fname = 'best_model_Amity_2023-6-8.csv'
# amity_model_fname = 'best_model_San_Antonio_2023-6-8.csv'

amity_model_data = [
                ('Amity', (45.11697099005726, -123.20202573006682), True),
                ('DaytonCutoffSolar', (45.168832884164075, -123.13668793938469), False),
                ('ValleyCreekSolar', (45.03245271909166, -123.09466606026315), False),
                ('ButlerSolar', (45.10106068680774, -123.41456045471486), False),
                # ('MillCreekSolar', (45.088307785035745, -123.42307867208085), False),
                ('RedPrarieSolar', (45.08715641433478, -123.41655553988588), False),

                # # for whatever reason this makes the whole thing explode
                # ('GrandeRondeSolar', (45.06344507542511, -123.61084728279289), False),

              ]


amity = SubstationModel('Amity',
                            amity_model_data,
                            training_start_date = datetime(2022, 1, 1) + timedelta(days=1),
                            # training_start_date = datetime(2023, 1, 1) - timedelta(days=200),
                            # training_end_date = datetime(2023, 6, 22),
                            # training_start_date = current_datetime - timedelta(days=90),
                            training_end_date = current_datetime,
                            prediction_start_date = prediction_start_date,
                            prediction_end_date = prediction_end_date,
                            site_id = '5ebb4527-edbd-11ed-bf8d-128dcacebd72',
                            forecast_id = "56178e67-0044-11ee-bbbf-aa678857fb1c",
                            arbiter_uname = uname,
                            arbiter_pwd = pwd,
                            # model_fname = amity_model_fname,
                            model_fname = 'regressor',
                            overwrite = True
                            )
    
amity.forecast_node_for_arbiter('Amity')

# except Exception as e:
#     print(e)
    
# ### DONALSON SUBSTATION ####

# try: 
    
#     print("------- DONALSONVILLE FORECAST -------")

#     # 10 AM GA = 7 AM PST DUE DATE
    
#     prediction_start_date = datetime(2023, month, day,5) # 1 AM in Georgia
#     prediction_end_date = prediction_start_date + timedelta(hours=23)
    
#     donalsonville_model_data = [
#                     ('Donalsonville', (21.442829733191395, -158.1853281893482), True),
#                     ('JakinSolar', (31.138863746325253, -85.03118409468937), False),
#                     ('DecaturSolar', (30.986638120780924, -84.62477997260771), False)
#                   ]
    
    
#     # donalsonville_model_fname = 'best_model_Donalsonville_2023-6-8.csv'
#     # donalsonville_model_fname = 'best_model_Waianae_2023-6-8.csv'
    
#     donalsonville = SubstationModel('Donalsonville',
#                                 donalsonville_model_data,
#                                 training_start_date = datetime(2022, 1, 1) + timedelta(days=1),
#                                 # training_start_date = datetime(2023, 5, 1) - timedelta(days=120),
#                                 # training_end_date = datetime(2023, 6, 19),
#                                 training_end_date = current_datetime,
#                                 prediction_start_date = prediction_start_date,
#                                 prediction_end_date = prediction_end_date,
#                                 site_id = '90c2a42c-f0ad-11ed-94b4-5edf5e2b3336',
#                                 forecast_id = "4647b078-0044-11ee-971c-22bbbfba48a8",
#                                 arbiter_uname = uname,
#                                 arbiter_pwd = pwd,
#                                 # model_fname = donalsonville_model_fname
#                                 model_fname = 'regressor',
#                                 overwrite = True
#                                 )
    
#     donalsonville.forecast_node_for_arbiter('Donalsonville')

# except Exception as e:
#     print(e)
    

# #### SAN ANTONIO SUBSTATION #####

# try:
        
#     print("------- SAN ANTONIO FORECAST -------")
    
#     # 10 AM TX = 8 AM PST DUE DATE
    
#     prediction_start_date = datetime(2023, month, day,6) # 1 AM SAn Antonio
#     prediction_end_date = prediction_start_date + timedelta(hours=23)
    
#     sanantonio_model_data = [
#                     ('San_Antonio', (29.461747984228385, -98.41624157225735), True),
#                     ('OCIAlamo1Solar', (29.271635783583502, -98.4558859752514), False),
#                     ('CPSBlueWingSolar', (29.24181153760114, -98.41880246326674), False),
#                     ('OCIAlamo2Solar', (29.482374895469594, -98.33868446297332), False)
#                   ]
    
#     # sanantonio_model_fname = 'best_model_San_Antonio_2023-6-8.csv'
    
#     sanantonio = SubstationModel('San_Antonio',
#                                 sanantonio_model_data,
#                                 training_start_date = datetime(2022, 5, 30) + timedelta(days=1),
#                                 # training_start_date = datetime(2023, 5, 30) - timedelta(days=120),
#                                 # training_end_date = datetime(2023, 6, 21),
#                                 training_end_date = current_datetime,
#                                 prediction_start_date = prediction_start_date,
#                                 prediction_end_date = prediction_end_date,
#                                 site_id = "8568f10f-eb8f-11ed-a556-128dcacebd72",
#                                 forecast_id = "4ea42e3b-0044-11ee-ad98-22bbbfba48a8",
#                                 arbiter_uname = uname,
#                                 arbiter_pwd = pwd,
#                                 # model_fname = sanantonio_model_fname
#                                 model_fname = 'regressor',
#                                 overwrite = True
#                                 )
    
#     sanantonio.forecast_node_for_arbiter('San_Antonio')

# except Exception as e:
#     print(e)
    
# ### WAIANAE SUBSTATION ####

# try: 
    
#     print("------- WAIANAE FORECAST -------")
    
#     # 10 AM HI = 1 PM PST DUE DATE
    
#     prediction_start_date = datetime(2023, month, day,11) # 1 AM Hawaii
#     prediction_end_date = prediction_start_date + timedelta(hours=23)
    
#     # waianae_model_fname = 'best_model_Waianae_2023-6-26.csv'
    
#     waianae_model_data = [
#                     ('Waianae', (21.442829733191395, -158.1853281893482), True),
#                     ('MilianiSolar', (21.427276574606115, -158.01911114704265), False),
#                     ('WaipioSolar', (21.452835566982312, -157.9881936598061), False),
#                     ('KuponoSolar', (21.329008066249028, -157.9950072825633), False),
#                     ('KawaiolaWind', (21.625181494356188, -158.0575848150004), False),
#                     ('KahukuWind', (21.6859319055306, -157.97046240290643), False)
#                   ]
    
#     waianae = SubstationModel('Waianae',
#                                 waianae_model_data,
#                                 training_start_date = datetime(2022, 5, 31) + timedelta(days=1),
#                                 # training_start_date = datetime(2023, 5, 31) - timedelta(days=120),
#                                 # training_end_date = datetime(2023, 6, 21),
#                                 training_end_date = current_datetime,
#                                 prediction_start_date = prediction_start_date,
#                                 prediction_end_date = prediction_end_date,
#                                 # site_id = '5ebb4527-edbd-11ed-bf8d-128dcacebd72' ,
#                                 site_id = 'c639b1f3-eb8f-11ed-802e-aec5a60999dc',
#                                 # forecast_id = "56178e67-0044-11ee-bbbf-aa678857fb1c",
#                                 forecast_id = '5d2d9c84-0044-11ee-acf5-22bbbfba48a8',
#                                 arbiter_uname = uname,
#                                 arbiter_pwd = pwd,
#                                 # model_fname = waianae_model_fname
#                                 model_fname = 'regressor',
#                                 overwrite = True
#                                 )
    
#     waianae.forecast_node_for_arbiter('Waianae')


# except Exception as e:
#     print(e)

# # # #### UPLOAD DATA ####
  
# # # print("------- UPLOADING DATA -------")

# # # try:
    
# # #     print("------- AMITY UPLOAD -------")
    
# # #     amity.upload_forecast_data()
# # # except Exception as e:
# # #     print(e)
    
# # # try:
# # #     print("------- DONALSONVILLE UPLOAD -------")
    
# # #     donalsonville.upload_forecast_data()
# # # except Exception as e:
# # #     print(e)
    
# # # try:
# # #     print("------- SAN ANTONIO UPLOAD -------")
    
# # #     sanantonio.upload_forecast_data()
# # # except Exception as e:
# # #     print(e)
    
# # # try:
# # #     print("------- WAIANAE UPLOAD -------")
    
# # #     waianae.upload_forecast_data()
# # # except Exception as e:
# # #     print(e)
    