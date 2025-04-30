import pandas as pd
from concurrent import futures

def read_csv(file_path):
    return pd.read_csv(file_path, index_col='time', parse_dates=True)

def resample_data(df, interval):
    return df.resample(interval).interpolate()

def main():
    file_paths = ['Waianae_solar_training.csv']
    resample_interval = '1h'  # Resample to a fixed 1-minute interval

    with futures.ThreadPoolExecutor() as executor:
        # Read and resample the data concurrently
        future_to_resampled = {executor.submit(read_csv, file_path): file_path for file_path in file_paths}
        resampled_data = [future.result().pipe(resample_data, resample_interval) for future in futures.as_completed(future_to_resampled)]

    # Merge the resampled data
    merged_data = pd.concat(resampled_data, axis=1).dropna()
    merged_data.to_csv('Waianae_solar_imputed.csv')

if __name__ == "__main__":
    main()
