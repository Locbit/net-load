import os
import pandas as pd
import zipfile
import re
import shutil
import glob

import pytz

from logging import info

'''
AusgridLoadData class:

So named (ausgrid_load_data) because this class is specifically for Ausgrid load data. 
The actual competition data and CAISO load data will be different and will need to
be processed in a significantly different manner.

This class contains functions for loading, processing, and concatenating 
load data files from Ausgrid. They are in a specific file format and need to 
be processed specially. See below website for ausgrid data:

https://www.ausgrid.com.au/Industry/Our-Research/Data-to-share/Distribution-zone-substation-data

This data is problematic because not all substations are included in the files for each year.
This may cause problems with data processing. 

The "Punchbowl 33" substation works well and is a good choice to use.

After the csv files are processed, they are read by the TrainingData class
to be cleaned in order to make them suitable for ML model training.
    
'''

class AusgridLoadData:
    def __init__(self, substation_name, model_name, file_path, start_date, end_date):
        # self.load_file = load_file
        # self.weather_file = weather_file        
        self.substation_name = substation_name
        
        self.model_name = model_name
        
        self.path = file_path
        self.data = pd.DataFrame()
        self.start_date = start_date
        self.end_date = end_date

        # get the data from the ausgrid data
        self.extract()
        self.rename()
        self.process_csv_files()
        self.concatenate_csv()
        self.concat_all_load_files()


    def extract(self):
        # Create a directory for the extracted zip files
        extracted_dir = os.path.join(self.path, "extracted")
        
        if not os.path.isdir(extracted_dir):
    
            os.makedirs(extracted_dir, exist_ok=True)
        
            for zip_file in glob.glob(os.path.join(self.path, "*.zip")):
                # Get the name of the directory to extract to
                extract_dir = os.path.join(extracted_dir, os.path.splitext(os.path.basename(zip_file))[0])
                os.makedirs(extract_dir, exist_ok=True)
        
                # Extract the zip file to the directory
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
        
                # Check if there are any directories within the extracted directory
                for subdir in os.listdir(extract_dir):
                    subdir_path = os.path.join(extract_dir, subdir)
                    if os.path.isdir(subdir_path):
                        # Move any files within the subdirectory to the base extracted directory
                        for file in os.listdir(subdir_path):
                            file_path = os.path.join(subdir_path, file)
                            if os.path.isfile(file_path):
                                
                                shutil.move(file_path, extract_dir)
        else:
            print("AusgridLoadData: Directory 'extracted' already exists, skipping CSV file extracting.")

    def rename(self):
        # Find the excel file containing the substation name in each directory
        training_data_dir = os.path.join(self.path, self.substation_name)
        
        if not os.path.exists(training_data_dir):
            # training_data_dir does not exist, create it and proceed with file processing
            os.makedirs(training_data_dir, exist_ok=True)
    
            extracted_dir = os.path.join(self.path, "extracted")
    
            # Find the excel file containing the substation name in each directory
            for extract_dir in os.listdir(extracted_dir):
                for file in os.listdir(os.path.join(extracted_dir, extract_dir)):
                    if file.endswith(".csv") and self.substation_name in file:
                        # Rename the file and copy it to the load_training_data directory
                        new_file = f"{self.substation_name}_{extract_dir}.csv"
                        shutil.copy(os.path.join(extracted_dir, extract_dir, file), os.path.join(training_data_dir, new_file))
        else:
            # training_data_dir already exists, skip file processing
            print(f"AusgridLoadData: {training_data_dir} already exists, skipping file processing")
    

    def process_csv_files(self):
            
        directory_path = f"{self.path}\{self.substation_name}"
    
        if not any(file.endswith(".load") for file in os.listdir(directory_path)):
            # No files ending with ".load" exist, proceed with CSV file processing
            for file_name in os.listdir(directory_path):
                if file_name.endswith('.csv'):
                    file_path = os.path.join(directory_path, file_name)
                    # df = pd.read_csv(file_path)
                    print("restructuring")
                    new_df = self.restructure_input_data(file_path)
                    new_file_path = os.path.join(directory_path, f"{file_name}.load")
                    new_df.to_csv(new_file_path)
        else:
            # Files ending with ".load" exist, skip CSV file processing
            print("AusgridLoadData: Processed files already exist, skipping CSV file processing")
            

    # def restructure_input_data(self, filename):
    #     # Re-structure input data wide CSV files into long pandas dataframes
    #     d2 = pd.read_csv(filename)
        
    #     d2.drop(['Zone Substation', 'unit', 'year'], inplace=True, axis=1)
        
    #     # rename the last column, which is always 24:00:00 because datetime cant accept those values
    #     d2 = d2.rename({d2.columns[-1]:'23:59'}, axis='columns')  # datetime can't accept 24:00 value!

    #     d2['Date'] = pd.to_datetime(d2['Date'], infer_datetime_format=True)
        
    #     d2 = d2.melt(id_vars=['Date'])
        
    #     d2['variable'] = d2['variable']
    #     d2['variable'] = pd.to_datetime(d2['variable'], infer_datetime_format=True)
    #     d2['variable'] = d2['variable'].dt.time
        
    #     d2 = d2.set_index(['Date', 'variable'])
    #     d2 = d2.sort_index(level=[0,1]).reset_index()
        
        
    #     d2['DT'] = d2.apply(lambda r: pd.datetime.combine(r['Date'], r['variable']), axis=1)
                
    #     # Adding timezone information and converting to UTC
    #     sydney_tz = pytz.timezone('Australia/Sydney')
    #     d2['DT'] = d2['DT'].dt.tz_localize(sydney_tz, nonexistent='shift_forward', ambiguous='shift_backward').dt.tz_convert('UTC')

        
    #     d2.set_index(d2['DT'], inplace=True)
    #     d2.drop(labels=['Date', 'variable', 'DT'], axis=1, inplace=True)
        
    #     d2 = d2.rename({'value':self.substation_name}, axis='columns')
        
    #     # Forward fill missing data
    #     d2.fillna(method='ffill', axis=0, inplace=True)
        
    #     # Resample data from 15min to 1hour level
    #     # (weather data is available only every hour)
    #     d2 = d2.resample('H').mean()
        
    #     return d2
    
    def restructure_input_data(self, filename):
        
        print("restructureing")
        # Re-structure input data wide CSV files into long pandas dataframes
        d2 = pd.read_csv(filename)
    
        d2.drop(['Zone Substation', 'unit', 'year'], inplace=True, axis=1)
    
        # rename the last column, which is always 24:00:00 because datetime cant accept those values
        d2 = d2.rename({d2.columns[-1]:'23:59'}, axis='columns')  # datetime can't accept 24:00 value!
    
        d2['Date'] = pd.to_datetime(d2['Date'], infer_datetime_format=True)
    
        d2 = d2.melt(id_vars=['Date'])
    
        d2['variable'] = d2['variable']
        d2['variable'] = pd.to_datetime(d2['variable'], infer_datetime_format=True)
        d2['variable'] = d2['variable'].dt.time
    
        d2 = d2.set_index(['Date', 'variable'])
        d2 = d2.sort_index(level=[0,1]).reset_index()
    
        d2['DT'] = d2.apply(lambda r: pd.datetime.combine(r['Date'], r['variable']), axis=1)
        
        # Adding timezone information and converting to UTC
        sydney_tz = pytz.timezone('Australia/Sydney')
        d2['DT'] = d2['DT'].dt.tz_localize(sydney_tz, nonexistent='shift_forward', ambiguous='NaT').dt.tz_convert('UTC')
    
        d2.set_index(d2['DT'], inplace=True)
        d2.drop(labels=['Date', 'variable', 'DT'], axis=1, inplace=True)
    
        


        d2 = d2.rename({'value':self.substation_name}, axis='columns')
    
        # Forward fill missing data
        d2.fillna(method='ffill', axis=0, inplace=True)
    
        
        
        # Resample data from 15min to 1hour level
        # (weather data is available only every hour)
        d2 = d2.resample('H').mean()
    
        d2.index = d2.index.strftime('%m/%d/%Y %H:%M')
        
        return d2


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
            
            # Write the combined data to the output file with year range
            combined_data.to_csv(output_filename, index=False)
            
            self.data = combined_data
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
    
