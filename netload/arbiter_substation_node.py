import os
import time
import timeit
import folium
import pickle
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from matplotlib import cm
from geopy.geocoders import Nominatim
from geopy import distance
# from bayes_opt import BayesianOptimization
from scipy import optimize

# Scikit-learn
from sklearn.svm import SVR
# from thundersvm import SVR
from sklearn.cluster import AgglomerativeClustering
from sklearn.linear_model import ElasticNetCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.feature_selection import SelectFromModel


# import tensorflow as tf
# from tensorflow import keras

import seaborn as sns

import joblib

# from keras.models import Sequential
# from keras.layers import Dense, Activation
# from keras.regularizers import l1_l2
# from keras.layers import Flatten
import numpy as np
# from keras.optimizers import Adam
# from bayes_opt import BayesianOptimization


from netload.weather_data import WeatherData
from netload.weather_forecast_data import WeatherForecastData
from netload.arbiter_load_data import ArbiterLoadData
from netload.gas_data import GasData

'''
SubstationNode class:

'''

class ArbiterSubstationNode:
    def __init__(self, substation_name, model_name, substation_loc, start_date, end_date, is_load_data = True):
        
        self.start_date = start_date
        self.end_date = end_date
        
        self.load_data = None
        
        self.substation_loc = substation_loc
        
        self.model_name = model_name
        
        # # set data path. we are using ausgrid data
        self.data_path = 'arbiter_data'
        
        self.substation_name = substation_name
        
        # Create instance of WeatherData class
        self.weather_data = WeatherData(substation_name,
                                   self.model_name,
                                   self.substation_loc,
                                   start_date, end_date)
        
        # Create instance of WeatherData class
        self.weather_forecast_data = WeatherForecastData(substation_name,
                                   self.model_name,
                                   self.substation_loc,
                                   start_date, end_date)
        
        self.training_data = None
        self.regressor_data = None
        

        
        self.full_data = pd.concat([self.weather_data.imputed_data, self.weather_forecast_data.imputed_data])

        if is_load_data:
                
            # create an instance of the LoadData class
            self.load_data = ArbiterLoadData(substation_name,
                                        self.model_name,
                                        self.data_path,
                                        self.substation_loc,
                                        start_date,
                                        end_date)
            
            # self.full_data = pd.concat([self.full_data, self.load_data.data])
            self.full_data = self.full_data.merge(self.load_data.data, on='DT', how='outer')
            


        if substation_name in self.full_data.columns:
            new_columns = [col if col == substation_name else '{}_{}'.format(col, substation_name) for col in self.full_data.columns]
        else:
            new_columns = ['{}_{}'.format(col, substation_name) for col in self.full_data.columns]
        
        self.full_data.columns = new_columns

        
        # # Create instance of GasData class
        # self.gas_data = GasData(substation_name,
        #                             self.model_name,                     
        #                             start_date, end_date)
        
        # # Create instance of SolarData class
        # self.solar_data = SolarData(substation_name,
        #                             self.model_name,                     
        #                             start_date, end_date)
        