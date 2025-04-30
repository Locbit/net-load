import pandas as pd
import numpy as np

from netload.weather_data import WeatherData
# from netload.ausgrid_load_data import AusgridLoadData

from netload.training_data import TrainingData

from netload.caiso_load_data import CAISOLoadData
# from netload.prediction_data import PredictionData
from netload.validation_data import ValidationData
from netload.weather_forecast_data import WeatherForecastData

# from netload.ausgrid_substation_node import AusgridSubstationNode
from netload.arbiter_substation_node import ArbiterSubstationNode

from meteostat import Point

from datetime import timedelta

from autots import AutoTS, create_regressor

import time

from autots.models.model_list import model_lists

import matplotlib.pyplot as plt

import os
import shutil

import pandas as pd
import pytz
from pytz import timezone
from solarforecastarbiter.io import api
from datetime import datetime, timedelta

# from autots.evaluator.auto_ts import fake_regressor



class SubstationModel:
    def __init__(self, model_name,
                 node_data,
                 training_start_date,
                 training_end_date,
                 prediction_start_date,
                 prediction_end_date,
                 site_id,
                 forecast_id,
                 arbiter_uname,
                 arbiter_pwd,
                 model_fname = 'fast_train',
                 load_type='arbiter',
                 validation=False,
                 overwrite = True):
        
        
        self.site_id = site_id
        self.forecast_id = forecast_id
        self.arbiter_uname = arbiter_uname
        self.arbiter_pwd = arbiter_pwd
        
        self.training_start_date = training_start_date
        self.training_end_date = training_end_date
        self.prediction_start_date = prediction_start_date
        self.prediction_end_date = prediction_end_date
        
        
        self.prob_forecast = None
        
        self.model_name = model_name
        
        
        self.model_fname = model_fname
        
        if overwrite == True:
            # Check if the directory exists
            if os.path.exists(self.model_name):
                # Delete the directory and its contents
                shutil.rmtree(self.model_name)
                print(f"The directory '{self.model_name}' has been deleted.")
            else:
                print(f"The directory '{self.model_name}' does not exist.")

            
        # Create an empty list to store the AusgridSubstationNode objects
        substation_nodes = []

        # Iterate over the list of node data
        for name, coordinates, is_load_data in node_data:
            
            # if load_type == 'ausgrid':
            #     # Create AusgridSubstationNode object with corresponding arguments
            #     sub_node = AusgridSubstationNode(name, self.model_name, Point(*coordinates), start_date, end_date)
            if load_type == 'arbiter':
                # Create AusgridSubstationNode object with corresponding arguments
                sub_node = ArbiterSubstationNode(name, self.model_name, coordinates, training_start_date, training_end_date, is_load_data)
          
            # Append the object to the ausgrid_nodes list
            substation_nodes.append(sub_node)
        
        self.model_runtime = None
        
        self.model = None
        self.prediction = None
        self.model_results = None
        self.validation_results = None
        
        self.nodes = substation_nodes
        
        self.node_names = [node.substation_name for node in self.nodes]


        
        model_dfs = [node.full_data for node in self.nodes]
        self.model_dfs = model_dfs[0].join(model_dfs[1:], how='outer')
        
        
        df = self.model_dfs
        
        # Identify the row where any NaN appears for the most recent time.
        first_nan_row = df.isna().any(axis=1).idxmax()
        
        # Split the DataFrame into two parts
        df1 = df.loc[:first_nan_row - pd.Timedelta('1H')]
        df2 = df.loc[first_nan_row:]
        df2 = df2.dropna(axis=1, how='all')
        
        # Split the DataFrame into two parts
        self.training_data = df1
        self.regressor_data = df2
        
        # sometimes there are NaNs at the very end of the regressor because the weather
        # forecast doesn't go that far ahead. drop those nans
        self.regressor_data.dropna(inplace=True)
        
        self.full_data = pd.concat([self.training_data, self.regressor_data])
        self.regressor_training_data = pd.concat([self.training_data, self.regressor_data])
        self.regressor_training_data = self.regressor_training_data.dropna(axis=1)

        self.regr_train = None
        self.regr_fcst = None
        # try:
        
        # if validation:
        #     # # create validation data for each node. The validation data
        #     # # will be the load for the end_data + 24 hours ahead
            
                
        #     for node in self.nodes:
        #         self.node_validation_data.append(
        #             ValidationData(node.substation_name,
        #                           self.model_name,
        #                           node.end_date,
        #                           self.prediction_end_date))
        
        try:
            self.train_and_forecast()
        except Exception as e:
            print(e)
        
        # if validation:
        #     self.validate()


            
    def combine_dataframes(self, dataframes, suffixes):
        combined_df = pd.DataFrame()
    
        for i, df in enumerate(dataframes):
            suffix = suffixes[i]
            df_with_suffix = df.copy()  # Create a copy of the dataframe
    
            # Check if the column name already contains the suffix
            suffix_columns = [col for col in df.columns if col.endswith(suffix)]
            for col in df.columns:
                if col not in suffix_columns:
                    new_col = col + "_" + suffix
                    df_with_suffix.rename(columns={col: new_col}, inplace=True)
    
            combined_df = pd.concat([combined_df, df_with_suffix], axis=1)
    
        return combined_df
    
    
    def drop_redundant_columns(self, df, tolerance=0.01):
        redundant_cols = []  # List to store redundant column names
    
        # Iterate over each column pairwise
        for i in range(df.shape[1]):
            for j in range(i + 1, df.shape[1]):
                col1 = df.iloc[:, i]
                col2 = df.iloc[:, j]
    
                # Calculate the percentage difference between the columns
                diff = abs((col1 - col2) / col1)
    
                # Check if the percentage difference exceeds the tolerance
                if (diff > tolerance).sum() == 0:
                    redundant_cols.append(df.columns[j])
    
        # Drop redundant columns from the dataframe
        df.drop(columns=redundant_cols, inplace=True)
    
        return df
    
    def train_and_forecast(self):
        df = self.training_data
        long = False

        # Start the timer
        start_time = time.time()

        if self.training_end_date < self.prediction_start_date:
            hours = pd.date_range(self.training_end_date, self.prediction_end_date, freq='H')
        else:
            hours = pd.date_range(self.prediction_start_date, self.prediction_end_date, freq='H')

        hours_df = pd.DataFrame({'Date': hours})

        forecast_length = int(len(hours_df))
        


        model_name = self.model_name
        node_name = self.model_name
        prediction_date = self.prediction_end_date
        
        
        # model_list = model_lists['fast_parallel_no_arima']
        model_list = model_lists['default']
        
        if 'VAR' in model_list:
            del model_list['VAR']
            
            

        
        if self.model_fname == 'default_train':
            
            print("no model file provided. training detaled model")
            # model used for forecasts
            model = AutoTS(
                forecast_length=forecast_length,
                frequency='H',
                prediction_interval=0.9,
                ensemble=None,
                # model_list=model_lists['fast'],  # "superfast", "default", "fast_parallel"
                # model_list = ['UnivariateMotif'],
                model_list = model_list,
                transformer_list="fast",  # "superfast",
                drop_most_recent=1,
                max_generations=8, # changed from 4 geenration to 8
                num_validations=4, # changed from 2 to 1
                validation_method="backwards",
                current_model_file=f"{model_name}/current_model_{node_name}_{prediction_date.year}-{prediction_date.month}-{prediction_date.day}"
            )
            
        elif self.model_fname == 'fast_train':
        
            print("no model file provided. training fast model")
            # TEST MODEL
            model = AutoTS(
                forecast_length=forecast_length,
                frequency='H',
                prediction_interval=0.9,
                ensemble=None,
                # model_list=model_lists['fast'],  # "superfast", "default", "fast_parallel"
                model_list = ['UnivariateMotif'],
                # model_list = "fast",
                transformer_list="superfast",  # "superfast",
                drop_most_recent=1,
                max_generations=1, # changed from 4 geenration to 8
                num_validations=1, # changed from 2 to 1
                validation_method="backwards",
                current_model_file=f"{model_name}/current_model_{node_name}_{prediction_date.year}-{prediction_date.month}-{prediction_date.day}"
            )
            
            print("model training complete.")
            
        elif self.model_fname == 'regressor':
        
            print("training & predicting w regressor")
            
            forecast_length = len(self.regressor_data)

            metric_weighting = {
                    'smape_weighting': 3,
                    'mae_weighting': 2,
                    'rmse_weighting': 2,
                    'made_weighting': 0.5,
                    'mage_weighting': 1,
                    'mle_weighting': 0,
                    'imle_weighting': 0,
                    'spl_weighting': 5,
                    'containment_weighting': 3,
                    'contour_weighting': 1,
                    'runtime_weighting': 0.05,
                }
                            
            # example future_regressor with some things we can glean from data and datetime index
            # note this only accepts `wide` style input dataframes
            # and this is optional, not required for the modeling
            self.regr_train, self.regr_fcst = create_regressor(
                self.training_data,
                # df,
                forecast_length=forecast_length,
                frequency='H',
                # drop_most_recent=True,
                # scale=True,
                # summarize="auto",
                # backfill="bfill",
                # fill_na="spline",
                # holiday_countries={"US": None},  # requires holidays package
                # encode_holiday_type=True,
                # datepart_method="simple_2",
            )
            
            print('regressor created')
            model = AutoTS(
                forecast_length=forecast_length,
                frequency='H',
                # prediction_interval=0.95,
                # ensemble=['simple', 'horizontal-min'],
                max_generations=4,
                num_validations=2,
                # validation_method='seasonal 168',
                model_list=['SectionalMotif'],
                models_mode='regressor',
                transformer_list='superfast',
                # models_to_validate=0.2,
                # drop_most_recent=1,
                # n_jobs='auto',
                metric_weighting=metric_weighting,
                verbose = 1
            )
            
            print("fitting model")
            
            model = model.fit(
                self.training_data,
                future_regressor=self.regr_train
            )


            print("model training complete.")
        else:
            print(f"loading model file {self.model_fname}")
            # on new training
            model = AutoTS(forecast_length=forecast_length,
                           frequency='H', max_generations=0,
                           num_validations=0, verbose=1)
            model = model.import_template(self.model_fname, method='only') # method='add on'
            print("Overwrite template is: {}".format(str(model.initial_template)))
            
            print("loaded model from file.")
    
        # NOT WORKING PROPERLY
        # try:
        #     self.future_regressor_train2d, self.future_regressor_forecast2d = fake_regressor(
        #         df,
        #         dimensions=18,
        #         forecast_length=forecast_length,
        #         date_col='DT' if long else None,
        #         # value_col='value' if long else None,
        #         # id_col='series_id' if long else None,
        #         drop_most_recent=model.drop_most_recent,
        #         aggfunc=model.aggfunc,
        #         verbose=model.verbose,
        #         )
        # except Exception as e:
        #     print('---REGRESSOR ERROR---')
        #     print(e)
        

        print("model fitting complete. createing forecasts for validation.")
        
        prediction = model.predict(future_regressor=self.regressor_data)
        forecasts_df = prediction.forecast
        
        # prediction = model.predict(future_regressor=regr_fcst, verbose=3)
        # # prediction = model.predict(verbose=3)
        
        # # point forecasts dataframe
        # forecasts_df = prediction.forecast
        
        forecasts_df.to_csv(f"{model_name}/current_model_{node_name}_{prediction_date.year}-{prediction_date.month}-{prediction_date.day}_forecast.csv")
        
        # upper and lower forecasts
        forecasts_up, forecasts_low = prediction.upper_forecast, prediction.lower_forecast

        # accuracy of all tried model results
        model_results = model.results()
        # and aggregated from cross validation
        validation_results = model.results("validation")
        
        # save a template of best models

        print("validation complete. exporting best model information")
        
        model.export_template(
            f"{model_name}/best_models_{node_name}_{prediction_date.year}-{prediction_date.month}-{prediction_date.day}.csv",
            models="best",
            n=5,
            max_per_model_class=6,
            include_results=True,
        )


        self.model = model
        self.prediction = prediction
        self.model_results = model_results
        self.validation_results = validation_results
        
        # End the timer
        end_time = time.time()
        
        # Calculate the elapsed time in seconds
        elapsed_time = end_time - start_time
        
        # Convert elapsed time to a datetime.timedelta object
        delta = timedelta(seconds=elapsed_time)
        
        self.model_runtime = delta
        
        # Format the elapsed time as HH:MM:SS
        elapsed_time_formatted = str(delta)
        
        # Print the elapsed time
        print(f"The model took {elapsed_time_formatted} to execute.")


    def validate(self):
        
        forecast = self.prediction.forecast

        for node in self.node_validation_data:
            # Extract validation_data from the node
            validation_data = node.validation_data
        
            for column in validation_data.columns:
                # Check if this column exists in the forecast DataFrame
                if column in forecast.columns:
                    # If it exists, create a new DataFrame with validation_data and forecast data
                    new_df = pd.DataFrame()
                    new_df[column] = validation_data[column]
                    new_df[column + '_forecast'] = forecast[column]
                    
                    # Calculate MAPE and add it as a new column
                    new_df[column + '_mape'] = np.abs((new_df[column] - new_df[column + '_forecast']) / new_df[column]) * 100
                    # smape calculateions are below
                    # new_df[column + '_mape'] = (2 * np.abs(new_df[column] - new_df[column + '_forecast']) / (np.abs(new_df[column]) + np.abs(new_df[column + '_forecast']))) * 100
                    # new_df[column + '_mape'] = (2 * np.abs(new_df[column] - new_df[column + '_forecast']) / (np.abs(new_df[column]) + np.abs(new_df[column + '_forecast']))) * 100


                    # Create a new figure and an axis
                    fig, ax1 = plt.subplots(figsize=(10,5))
                    
                    # Plot actual data and forecast on the first y-axis
                    ax1.plot(new_df.index, new_df[column], label=column)
                    ax1.plot(new_df.index, new_df[column + '_forecast'], label=column + '_forecast')
                    ax1.set_ylabel('MW')  # Set label for the first y-axis
                    ax1.legend(loc='upper left')  # Place the legend at the upper left corner
                    ax1.grid(True, which='both')


                    # Create a second y-axis that shares the same x-axis
                    ax2 = ax1.twinx()
                    ax2.plot(new_df.index, new_df[column + '_mape'], label=column + '_mape', color='red', marker = 'o', linestyle='None')
                    ax2.set_ylabel('MAPE (%)')  # Set label for the second y-axis
                    ax2.legend(loc='upper right')  # Place the legend at the upper right corner
                    ax2.set_ylim([0, 20])
                    # ax2.grid(True, which='both')

                    # Add a title
                    plt.title(column + ' forecast and MAPE, avg MAPE = ' + str(round(np.mean(new_df[column + '_mape']),2)))


                    ax1.grid(True, which='both')


                    # Show the plot
                    plt.show()

                    # Append the new DataFrame to the node
                    node.forecast = new_df

        # Create an empty list to hold all forecast DataFrames
        forecast_dfs = []
        
        # Assuming node_validation_data is your list of Ausgridnode instances
        for node in self.node_validation_data:
            # Add the forecast dataframe to the list
            forecast_dfs.append(node.forecast)
        
        # Concatenate all the dataframes along columns
        combined_df = pd.concat(forecast_dfs, axis=1)
        
        # Now write the combined_df to a CSV file
        
        start_date = self.node_validation_data[0].start_date
             
        data_filename = f"{self.model_name}/forecast_{start_date.year}-{start_date.month}-{start_date.day}.csv"

        combined_df.to_csv(data_filename)


    def forecast_node_for_arbiter(self, node_name, prediction_dates_only = True, plot=False):
        
        print("creating forecasts for prediction")
        
        # Start the timer
        start_time = time.time()
        
        model = self.model
    
        # Initialize an empty DataFrame
        new_df = pd.DataFrame()

        intervals = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        prediction = model.predict(prediction_interval=intervals, future_regressor=self.regressor_data,verbose=3)
        # prediction = model.predict(prediction_interval=intervals, verbose=3)
        
        print(prediction)
        print("forecasts complete.")
        
        # Create a list of hours between the start and end dates
        # forecast_dates = pd.date_range(self.prediction_start_date, self.prediction_end_date, freq='H', utc=True)

        utc_tz = pytz.UTC
        forecast_dates = pd.date_range(
            start=self.prediction_start_date,
            end=self.prediction_end_date,
            freq='H',
            tz=utc_tz
        )
        # print('forecast dates')        

        # Create a DataFrame with the 'hours' list
        forecast_dates = pd.DataFrame({'DT': forecast_dates})
        # print(forecast_dates)        
        
        # Loop over each entry in the dictionary
        for key, predictionObject in prediction.items():
            # Extract the 'load' column from the forecast DataFrame
            
            load_series = predictionObject.upper_forecast[node_name]
            
            # load_series = load_series[(load_series.index > self.prediction_start_date) & (load_series.index < self.prediction_end_date)]

            # if prediction_dates_only == True:
   
            load_series.index = pd.to_datetime(load_series.index)
            forecast_dates['DT'] = pd.to_datetime(forecast_dates['DT'])
            load_series = load_series[load_series.index.isin(forecast_dates['DT'])]

            print(load_series)
            
            new_key = f"p{int(float(key)*100)}"
            
            # Add the series to the new DataFrame, renaming it according to the dictionary key
            new_df[new_key] = load_series
            
       
        
        # Convert the index to UTC and format it as ISO 8601
        new_df.index = pd.to_datetime(new_df.index, unit='s', utc=True).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
        # Rename the index column to 'timestamp'
        new_df.index.name = 'timestamp'
        
        self.prob_forecast = new_df
        
        data_filename = f"{self.model_name}/prob_forecast_{node_name}_{self.prediction_end_date.year}-{self.prediction_end_date.month}-{self.prediction_end_date.day}.csv"
    
        new_df.to_csv(data_filename)
        
        if plot == True:
            df = new_df
            # Create a figure and axis
            fig, ax = plt.subplots()
            
            # Plot the columns with different line styles and markers
            for i, column in enumerate(df.columns):
                ax.plot(df[column], label=column)
            
            # Set the legend
            ax.legend()
            
            # Show the plot
            plt.show()
            
    
        # End the timer
        end_time = time.time()
        
        # Calculate the elapsed time in seconds
        elapsed_time = end_time - start_time
        
        # Convert elapsed time to a datetime.timedelta object
        delta = timedelta(seconds=elapsed_time)
        
        
        # Format the elapsed time as HH:MM:SS
        elapsed_time_formatted = str(delta)
        
        # Print the elapsed time
        print(f"The forecasts took {elapsed_time_formatted} to execute.")
    

    def upload_forecast_data(self):
        
        uname = self.arbiter_uname
        pwd = self.arbiter_pwd
        model_name = self.model_name
        node_name = self.model_name
        site_id = self.site_id
        forecast_id = self.forecast_id
        prediction_date = self.prediction_end_date
        
        data_filename = f"{model_name}/prob_forecast_{node_name}_{prediction_date.year}-{prediction_date.month}-{prediction_date.day}.csv"
    
        df = pd.read_csv(data_filename)
    
        # get api token
        token = api.request_cli_access_token(uname, pwd)
        session = api.APISession(token, base_url="https://api.forecastarbiter.com")
    
        arbiter_forecast = session.get_probabilistic_forecast(forecast_id)
        forecast_ids = [item.forecast_id for item in arbiter_forecast.constant_values]
    
        # prepare data
        df.set_index(df.columns[0], inplace=True)
        df.index = pd.to_datetime(df.index)
    
        # upload data
        for i, forecast_id in enumerate(forecast_ids):
            col = df.columns[i]  # Get the column name/index from the DataFrame
            forecast_series = df[col]
            # print(f"{forecast_id}, {forecast_series}")
            session.post_probabilistic_forecast_constant_value_values(forecast_id, forecast_series)
            
        print('forecast upload complete')
