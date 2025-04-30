from datetime import datetime
from meteostat import Hourly
from meteostat import Point
import pandas as pd
import pytz
import os

from concurrent import futures

import yfinance as yf

'''
GasData class:
    
NOT READY FOR PRIME TIME BUT CLOSE!

ISSUES:
    yfinance price requests for weekends return nothing or NaNs
    if a price is requested and that date is on a weekend, the price needs to be the closing price from Friday (or the last close price of the market)
    
    The imputation functions here need to be removed, or just used in the training data class, or used in both
    
    This class is a mess
    
'''


class GasData:
    def __init__(self, substation_name, model_name, start_date, end_date, ticker = 'NG=F'):
        
        
        self.substation_name = substation_name
        self.model_name = model_name
        self.start_date = start_date
        self.end_date = end_date
        self.data = pd.DataFrame()
        
        self.ticker = ticker
        
        self.data_filename = f"{self.model_name}/{self.substation_name}/{self.substation_name}_{self.start_date.year}{self.start_date.month}{self.start_date.day}"\
            f"_{self.end_date.year}{self.end_date.month}{self.end_date.day}_gas.csv"
            
        # Extract the directory path from the data filename
        directory = os.path.dirname(self.data_filename)
        
        # Create the directories if they don't exist
        os.makedirs(directory, exist_ok=True)

        # get this data and put it to a csv
        self.get_gas_data()
        
        self.impute_financial_data()

        
    def get_gas_data(self):
        
        # Set the start and end dates
        sdate = self.start_date
        edate = self.end_date
        
        ticker = self.ticker
        
        # Create an empty DataFrame to store the ETF data
        etf_prices = pd.DataFrame()
        
        # Loop over each ETF and get the hourly data

        # Get the ticker data
        tickerData = yf.Ticker(ticker)
    
        # Get the hourly data
        s = tickerData.history(period='1d', start=sdate, end=edate)

        # Add the data to the DataFrame
        etf_prices['gas'] = s['Open']
        
        etf_prices = etf_prices.rename_axis('DT')

        # Resample the DataFrame to fill missing dates
        etf_prices = etf_prices.resample('D').ffill()
        
        # Forward fill the missing values
        etf_prices['gas'].fillna(method='ffill', inplace=True)
        
        # Reset the index to bring 'DT' back as a column
        etf_prices.reset_index(inplace=True)
        
        etf_prices.set_index('DT', inplace=True)

        etf_prices.index = etf_prices.index.tz_convert('UTC')
        
        etf_prices.index = etf_prices.index.strftime('%m/%d/%Y %H:%M')



        data_filename = self.data_filename
            
        # file_path = os.path.join(self.substation_name, data_filename)

        etf_prices.to_csv(data_filename)
        
    
    def read_csv(self, file_path):
        df = pd.read_csv(file_path)
        df['DT'] = pd.to_datetime(df['DT'])
        df.set_index('DT', inplace=True)
        return df
    
    
    
    def resample_data(self, df, interval):
        return df.resample(interval).interpolate()
    
    def impute_financial_data(self):
        file_paths = [self.data_filename]
        resample_interval = '1h'  # Resample to a fixed 1-minute interval
    
        with futures.ThreadPoolExecutor() as executor:
            # Read and resample the data concurrently
            future_to_resampled = {executor.submit(self.read_csv, file_path): file_path for file_path in file_paths}
            resampled_data = [future.result().pipe(self.resample_data, resample_interval) for future in futures.as_completed(future_to_resampled)]
    
        # Merge the resampled data
        merged_data = pd.concat(resampled_data, axis=1).dropna()
        
        data_filename = self.data_filename
            
        merged_data.to_csv(data_filename)