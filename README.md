# net-load

This project is for Locbit's entry to the Net Load Forecasting Competition.

## Installation

1. Clone the repository: `git clone https://github.com/boianspassovlocbit/net-load`

Requires the meteostat library: https://dev.meteostat.net/python/

For now the load data is taken from Ausgrid because that is the only available data so far:
https://www.ausgrid.com.au/Industry/Our-Research/Data-to-share/Distribution-zone-substation-data

## Usage

See predict_load.py script.

WeatherData and LoadData classes are created to get the weather and grid load data. For now, all grid load data is taken from Ausgrid. In the future we expect to be able to do this with load data from the competition, or for CAISO data

The weather and grid load data are passed into a TrainingData class which cleans the data.

Each class saves their output to csv files.

Methods within the SubstationModel class create a ML model and train it with the data from the TrainingData class. The model and predictions are saved to a file.

Classes that pull data from the internet (like the WeatherData class) could possibly get your client blocked if you try and call them too often.

______

WeatherData class:

This class contains functions for retrieving weather data from the online meteostat library
and for saving it to csv files. These files will then be used later along with the grid load
data files in the TrainingData class to be cleaned and maide suitable for ML training.

NOTE: using get_hourly_data() pulls data from the meteostat server. So if you do this
too often, you may get temporarily blocked.

---

LoadData class:

This class contains functions for loading, processing, and concatenating 
load data files from Ausgrid. They are in a specific file format and need to 
be processed specially. See below website for ausgrid data:

https://www.ausgrid.com.au/Industry/Our-Research/Data-to-share/Distribution-zone-substation-data

This data is problematic because not all substations are included in the files for each year.
This may cause problems with data processing. 

The "Punchbowl 33" substation works well and is a good choice to use.

After the csv files are processed, they are read by the TrainingData class
to be cleaned in order to make them suitable for ML model training.

---

TrainingData class:

This class takes the grid load data and the weather data, filters out all
data between the start date and end date. This filtering is mainly done 
because of the format of Ausgrid data, for example, data for FY2022 actually contains data
between 5/2021 and 5/2022 and this doesn't line up with data from meteostat.
This causes problems during imputation.

After the files are loaded and filtered, they are imputed and saved to a csv file.

---

SubstationModel class:

This class reads the training data file, processes it for training, 
trains a model and saves it, makes a prediction, and saves that prediction.

## License
Members of Locbit Net Load Forecasting Competition Team:
Ross MacDonald, Boian Spassov, Gleb Marasin, Natasha Morgan, Brian Hafner
