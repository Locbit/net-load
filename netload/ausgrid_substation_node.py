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


import tensorflow as tf
from tensorflow import keras

import seaborn as sns

import joblib

from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.regularizers import l1_l2
from keras.layers import Flatten
import numpy as np
from keras.optimizers import Adam
# from bayes_opt import BayesianOptimization


from netload.weather_data import WeatherData
from netload.ausgrid_load_data import AusgridLoadData

'''
SubstationNode class:

'''

class AusgridSubstationNode:
    def __init__(self, substation_name, model_name, substation_loc, start_date, end_date):
        
        self.start_date = start_date
        self.end_date = end_date
        
        self.model_name = model_name
        
        # # set data path. we are using ausgrid data
        self.data_path = 'ausgrid_data'
        
        self.substation_name = substation_name
        
        # create an instance of the LoadData class
        self.load_data = AusgridLoadData(substation_name,
                                    self.model_name,
                                    self.data_path,
                                    start_date,
                                    end_date)

        # Create instance of WeatherData class
        self.weather_data = WeatherData(substation_name,
                                        self.model_name,
                                   substation_loc,
                                   start_date, end_date)
        