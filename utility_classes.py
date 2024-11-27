import pandas as pd
import requests
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class ApiFetcher:
	@staticmethod
	def fetch_data(url:str, payload:dict)->dict:	
		try:
			response = requests.post(url, json=payload)
			response.raise_for_status()
			return response.json()	
		except requests.exceptions.RequestException as e:
			print(f'API fetch error: {e}')

class Transformer:
	@staticmethod
	def transform(df:pd.DataFrame, parameter:str)->pd.DataFrame:
		match parameter:
			case 'temperature-2m':
				df_transformed = round(df-273.15,1)
				return df_transformed
			case 'pressure-surface' :
				df_transformed = round(df/100,1)
				return df_transformed
			case 'global-radiation-flux':
				df_transformed =  round(df.diff()/3600, 1)
				return df_transformed
			case 'total-precipitation':
				df_transformed = round(df.diff(), 1)
				return df_transformed
			case _:
				df_transformed = round(df, 1)
				return df_transformed


class DataProcessor(ABC):
	@abstractmethod
	def process_data():
		pass

class HistoricalDataProcessor(DataProcessor):
	def process_data(self, jsonData:dict, tranformer:Transformer)->pd.DataFrame:
		if not jsonData:
			print("Error: Missing json data")
		try:
			timestamps = [feature['properties']['from'][:13] for feature in jsonData]
			y_data = [feature['properties']['value'] for feature in jsonData]
			if not timestamps:
				raise Exception("Error: Missing data for timestamps")
			if not y_data:
				raise Exception("Error: Missing data for values")
		except KeyError as e:
			raise KeyError(f'Missing expected key in jsonData: {e}')
		
		df = pd.DataFrame({'value':y_data}, index=timestamps)
		df.index.name = "HourUTC"
		return df

class ForecastDataProcessor(DataProcessor):
	def process_data(self, jsonData:dict, transformer:Transformer)->pd.DataFrame:
		if not jsonData:
			print("Error: Missing json data")
			return pd.DataFrame()
		try:
			parameter = list(jsonData['parameters'].keys())[0]
			timestamps = jsonData.get('domain', {}).get('axes', {}).get('t', {}).get('values', [])
			if not parameter or not timestamps:
				raise KeyError('Missing parameter or timestamps in jsonData')
			spliced_timestamps = [s[:13] for s in timestamps]
			values = jsonData.get('ranges', {}).get(parameter, {}).get('values', [])
			if not values:
				raise KeyError(f'Missing or empty values for parameter "{parameter}"')
		except KeyError as e:
			raise KeyError(f'Missing expected key in jsonData: {e}')
		# Create a DataFrame for the JSON dataset
		df = pd.DataFrame({parameter: values}, index=spliced_timestamps)
		df.index.name = "HourUTC"
		df_transformed = transformer.transform(df, parameter)
		return df_transformed


class DataContainer:
	def __init__(self, url:str=None, payload:str=None, apiFetcher:ApiFetcher=None, dataProcessor:DataProcessor=None, transformer:Transformer=None):
		self.url:str = url
		self.payload:dict = payload
		self.transformer = transformer
		self.apiFetcher = apiFetcher
		self.dataProcessor= dataProcessor
		self.df:pd.DataFrame=None

	def create_data(self):
		json_data = self.apiFetcher.fetch_data(self.url, self.payload)
		if json_data is None:
			print(json_data)
			print("No data available")
		else:
			self.df = self.dataProcessor.process_data(json_data, self.transformer)


### TEST AREA ###
def main()->None:
	apiFetcher = ApiFetcher()
	historicalProcessor = HistoricalDataProcessor()
	forecastProcessor = ForecastDataProcessor()

	weather_url = "http://127.0.0.1:8000/weather"
	historical_parameters = [
							'mean_relative_hum',
							'mean_temp', 
							'mean_wind_speed', 
							'mean_pressure', 
							'mean_radiation', 
							'acc_precip', 
							'mean_cloud_cover']

#
	forecast_url = 'http://127.0.0.1:8000/forecast'
	coords = 'POINT(9.5 56.0)'
	edr_parameters = [
						'relative-humidity-2m',  # mean_relative_hum
    					'temperature-2m',        # mean_temp
    					'wind-speed-10m',        # mean_wind_speed
    					'pressure-surface',  # mean_pressure
    					'direct-solar-exposure',       # mean_radiation
    					'total-precipitation', # acc_precip
    					'high-cloud-cover',
    					'medium-cloud-cover',
    					'low-cloud-cover'           # mean_cloud_cover
						]
	high_payload={
			'coords':coords,
			'crs':'crs84',
			'parameter':'high-cloud-cover'
			}
	med_payload={
			'coords':coords,
			'crs':'crs84',
			'parameter':'medium-cloud-cover'
			}
	low_payload={
			'coords':coords,
			'crs':'crs84',
			'parameter':'low-cloud-cover'
			}
	#forecast_container = DataContainer(forecast_url, payload, apiFetcher,forecastProcessor)
	#forecast_container.create_data()
	#forecasts.append(forecast_container)
	solar_payload={
				'coords':coords,
				'crs':'crs84',
				'parameter':'total-precipitation' 
				}
	solar_data= apiFetcher.fetch_data(forecast_url, solar_payload)
	solar_df = forecastProcessor.process_data(solar_data, 'solar_radiation')
	
	pd.set_option('display.max_rows', None)
	print(solar_df)
	#high_cloud_data = apiFetcher.fetch_data(forecast_url, high_payload)
	#med_cloud_data = apiFetcher.fetch_data(forecast_url, med_payload)
	#low_cloud_data = apiFetcher.fetch_data(forecast_url, low_payload)
	#json_list = [high_cloud_data, med_cloud_data, low_cloud_data]
	#merged_df = forecastProcessor.process_data(json_list,'mean')
	#print(merged_df)

	#for forecast in forecasts:
	#	print(forecast.payload['parameter'])
		
							
if __name__ =='__main__':
	main()