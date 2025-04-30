from autots.datasets import load_hourly
from autots.evaluator.auto_ts import fake_regressor
from autots import AutoTS, create_regressor
import pandas as pd
from autots import long_to_wide

long = False
df = load_hourly(long=long)

df.drop(df.index[:10000], inplace=True)


df2 = df
forecast_length = 14

df = df.drop(df.tail(forecast_length).index)

# example future_regressor with some things we can glean from data and datetime index
# note this only accepts `wide` style input dataframes
# and this is optional, not required for the modeling
regr_train, regr_fcst = create_regressor(
    df.drop('traffic_volume', axis=1),
    # df,
    forecast_length=forecast_length,
    # frequency='H',
    # drop_most_recent=True,
    # scale=True,
    # summarize="auto",
    # backfill="bfill",
    # fill_na="spline",
    # holiday_countries={"US": None},  # requires holidays package
    # encode_holiday_type=True,
    # datepart_method="simple_2",
)


# # remove the first forecast_length rows (because those are lost in regressor)
# df = df.iloc[forecast_length:]
# regr_train = regr_train.iloc[forecast_length:]

# # regr_fcst['traffic_volume'] = float('nan')
# # # regr_train = regr_train.drop('GS10', axis=1)
# # # regr_fcst = regr_fcst.drop('GS10', axis=1)

model = AutoTS(
    forecast_length=forecast_length,
    frequency='H',
    # prediction_interval=0.95,
    # ensemble=['simple', 'horizontal-min'],
    max_generations=1,
    num_validations=1,
    # validation_method='seasonal 168',
    model_list=['SectionalMotif'],
    models_mode='regressor',
    # transformer_list='all',
    # models_to_validate=0.2,
    # drop_most_recent=1,
    # n_jobs='auto',
    verbose = 1
)


model = model.fit(
    df,
    future_regressor=regr_train,
)


prediction = model.predict(future_regressor=regr_fcst)
forecasts_df = prediction.forecast

print(model)