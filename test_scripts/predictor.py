# import pandas as pd
# # also: _hourly, _daily, _weekly, or _yearly
# from autots.datasets import load_monthly

# df_long = pd.read_csv('Amity_for_forecast.csv', parse_dates=True)
# df_long['DT'] = pd.to_datetime(df_long['DT'])



# from autots import AutoTS

# # model = AutoTS(
# #     # forecast_length=3,
# #     frequency='infer',
# #     ensemble='simple',
# #     max_generations=5,
# #     num_validations=2,
# # )
# # model = model.fit(df_long, date_col='DT', value_col='Amity')


# model = AutoTS(
#     # forecast_length=forecast_length,
#     frequency='H',
#     prediction_interval=0.9,
#     ensemble=None,
#     # model_list=model_lists['fast'],  # "superfast", "default", "fast_parallel"
#     model_list = 'default',
#     # model_list = model_list,
#     transformer_list="fast",  # "superfast",
#     drop_most_recent=1,
#     max_generations=4, # changed from 4 geenration to 8
#     num_validations=2, # changed from 2 to 1
#     validation_method="backwards",
#     # current_model_file=f"{model_name}/current_model_{node_name}_{prediction_date.year}-{prediction_date.month}-{prediction_date.day}"
# )


# # # Print the description of the best model
# print(model)

from autots.datasets import load_monthly
from autots.evaluator.auto_ts import fake_regressor
from autots import AutoTS

long = False
df = load_monthly(long=long)
forecast_length = 14
model = AutoTS(
    forecast_length=forecast_length,
    frequency='infer',
    validation_method="backwards",
    max_generations=2,
)
future_regressor_train2d, future_regressor_forecast2d = fake_regressor(
    df,
    dimensions=4,
    forecast_length=forecast_length,
    date_col='datetime' if long else None,
    value_col='value' if long else None,
    id_col='series_id' if long else None,
    drop_most_recent=model.drop_most_recent,
    aggfunc=model.aggfunc,
    verbose=model.verbose,
)

model = model.fit(
    df,
    future_regressor=future_regressor_train2d,
    date_col='datetime' if long else None,
    value_col='value' if long else None,
    id_col='series_id' if long else None,
)
