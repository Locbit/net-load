import os
import pandas as pd
import zipfile
import re
import shutil
import glob

import pytz

from tzwhere.tzwhere import tzwhere

from logging import info

from netload.imputer import Imputer

'''
ArbiterLoadData class:

    
'''

class ArbiterLoadData:
    def __init__(self, substation_name, model_name, file_path, substation_loc, start_date, end_date):
        # self.load_file = load_file
        # self.weather_file = weather_file        
        self.substation_name = substation_name
        
        self.substation_loc = substation_loc
        
        self.model_name = model_name
        
        self.path = file_path
        self.data = pd.DataFrame()
        self.start_date = start_date
        self.end_date = end_date


        # self.read_csv_file()

        # get the data from the ausgrid data
        # self.extract()
        # self.rename()
        self.process_csv_files()
        self.concatenate_csv()
        
        
        # self.concat_all_load_files()



    def process_csv_files(self):
            
        directory_path = f"{self.path}\{self.substation_name}"
    
    # if not any(file.endswith(".load") for file in os.listdir(directory_path)):
        # No files ending with ".load" exist, proceed with CSV file processing
        for file_name in os.listdir(directory_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(directory_path, file_name)
                # df = pd.read_csv(file_path)
                print("restructuring")
                new_df = self.restructure_input_data(file_path)
                new_file_path = os.path.join(directory_path, f"{file_name}.load")
                new_df.to_csv(new_file_path)
    # else:
    #     # Files ending with ".load" exist, skip CSV file processing
    #     print("AusgridLoadData: Processed files already exist, skipping CSV file processing")
        

    def restructure_input_data(self, filename):
                
        print("restructureing")
                
        
        # Use skiprows to skip the first two lines
        df = pd.read_csv(filename, skiprows=2)
        
        # If the timestamp column is not automatically recognized as a datetime object, convert it
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%dT%H:%M:%S%z')
        
       
        # Rename the 'value' column to 'substation_name' and 'timestamp' to 'DT'
        df = df.rename(columns={'value': self.substation_name,
                                # 'quality_flag':f"quality_flag_{self.substation_name}",
                                'timestamp': 'DT'})
        
        # Drop the 'quality_flag' column
        df = df.drop(columns=['quality_flag'])

        latitude = self.substation_loc[0]
        longitude = self.substation_loc[1]
        
        tz_str = tzwhere().tzNameAt(latitude, longitude)

        # Adding timezone information and converting to UTC
        timezone = pytz.timezone(tz_str)
        # df['DT'] = df['DT'].dt.tz_localize(timezone, nonexistent='shift_forward', ambiguous='NaT').dt.tz_convert('UTC')
        df['DT'].dt.tz_convert(timezone).dt.tz_convert('UTC')
        
        # d2.set_index(d2['DT'], inplace=True)

        # Ensure self.start_date and self.end_date are timezone-aware
        self.start_date = self.start_date.replace(tzinfo=pytz.UTC)
        self.end_date = self.end_date.replace(tzinfo=pytz.UTC)

        # self.start_date  = df['DT'].min()
        # self.end_date  = df['DT'].max()
        
        # Set 'DT' as the index
        df = df.set_index('DT')
        df = df[(df.index >= self.start_date) & (df.index <= self.end_date)]

        df.index = df.index.strftime('%m/%d/%Y %H:%M')

        
        return df


    def concatenate_csv(self):
        # Create an empty dataframe to store the concatenated data
        combined_data = pd.DataFrame()
        
        # create the directory_path folder if it doesn't exist
        if not os.path.exists(f"{self.model_name}\{self.substation_name}"):
            os.makedirs(f"{self.model_name}\{self.substation_name}")
        
        output_filename = f"{self.model_name}\{self.substation_name}\{self.substation_name}_{self.start_date.year}_{self.end_date.year}_load.csv"
        
        if not os.path.exists(output_filename):
            # output file does not exist, proceed with CSV file processing
            # Loop through all files in the current directory
            for filename in os.listdir(f"{self.path}\{self.substation_name}"):
                # Check if the file is a CSV file and contains a 4-digit year number
                if filename.endswith(".load") and re.search(r"\d{4}", filename):
                    # Extract the year from the filename using regular expressions
                    year = re.findall(r"\d{4}", filename)[0]
                    year = int(year)
                    
                    # Check if the year is within the specified range
                    if year >= self.start_date.year and year <= self.end_date.year:
                        
                        try:
                            # Load the data from the CSV file
                            year_data = pd.read_csv(f"{self.path}\{self.substation_name}\{filename}")
                            
                            # Append the data to the combined dataframe
                            combined_data = pd.concat([combined_data, year_data])
                            combined_data = combined_data.loc[:, ['DT', f"{self.substation_name}"]]
                        except Exception as e:
                            info("AusgridLoadData: Couldn't find file to concatenate")
                            continue
            
            
            # imputer = Imputer(combined_data, resample_interval = '1h')
            # combined_data = imputer.process_dataframes()
            
            # Write the combined data to the output file with year range
            combined_data.to_csv(output_filename, index=False)
            
            self.data = combined_data
            self.data['DT'] = pd.to_datetime(self.data['DT'])
            self.data['DT'] = self.data['DT'].dt.tz_localize('UTC')
            self.data.set_index('DT', inplace=True)
            # self.data.index = self.data.index.strftime('%m/%d/%Y %H:%M')
            # self.data.index = self.data.index.strftime('%Y-%m-%d %H:%M:%s')

        else:
            # output file already exists, skip file processing
            print(f"AusgridLoadData: Prepared data for {self.substation_name} already exists, skipping file processing")
    

    def concat_all_load_files(self):
        # Create an empty dataframe to store the concatenated data
        combined_data = pd.DataFrame()
        
        output_filename = f"{self.path}\{self.substation_name}_all_load.csv"
        load_path = f"{self.path}\{self.substation_name}"
        
        if not os.path.exists(output_filename):
            # Get all the ".load" files in the current directory
            load_files = [f for f in os.listdir(load_path) if f.endswith('.load')]
            
            # Sort the files by filename
            load_files.sort()
        
            
            # Initialize an empty list to store the dataframes
            dfs = []
            
            # Loop over the files and read them into dataframes
            for filename in load_files:
                
                
                df = pd.read_csv(load_path + f"\\{filename}")
                dfs.append(df)
            
            # Concatenate the dataframes
            result = pd.concat(dfs)
            
            # Write the result to a new CSV file
            result.to_csv(f"{self.model_name}\{self.substation_name}\{self.substation_name}_all_load.csv", index=False)
        else:
            # output file already exists, skip file processing
            print(f"AusgridLoadData: Complete concatenated load data already exists - skipping")
    
