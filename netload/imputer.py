import pandas as pd
from concurrent import futures

class Imputer:
    def __init__(self, df_list, resample_interval='1h'):
        self.df_list = df_list
        self.resample_interval = resample_interval

    @staticmethod
    def resample_data(df, interval):
        return df.resample(interval).interpolate()

    def process_dataframes(self):
        with futures.ThreadPoolExecutor() as executor:
            # Resample the data concurrently
            future_to_resampled = {executor.submit(self.resample_data, df, self.resample_interval): df for df in self.df_list}
            resampled_data = [future.result() for future in futures.as_completed(future_to_resampled)]

        # Merge the resampled data
        self.merged_data = pd.concat(resampled_data, axis=1).dropna()
        return self.merged_data

