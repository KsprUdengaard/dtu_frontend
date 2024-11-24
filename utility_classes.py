import pandas as pd
import requests
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class ApiFetcher:
	@staticmethod
	def fetch_data(url, payload)->dict:	
		response = requests.post(url, json=payload)
		if response.status_code != 200:
			print(response.status_code)
			print(response.text)
			return None	
		else:
			print(response.status_code)
			return response.json()

class DataProcessor(ABC):
	@abstractmethod
	def process_data(jsonData: dict)->pd.DataFrame:
		pass

class HistoricalDataProcessor(DataProcessor):
	@staticmethod
	def process_data(jsonData: dict)->pd.DataFrame:
		if not jsonData:
			raise Exception("Error: Missing json data")
			return None  # Explicit return for empty or invalid data
		else:
			timestamps = [feature['properties']['from'][:13] for feature in jsonData]
			y_data = [feature['properties']['value'] for feature in jsonData]
		if not timestamps and y_data:
			raise Exception("Error: Missing data for timestamps or values.")
		else:
			df = pd.DataFrame({'value':y_data}, index=timestamps)
			df.index.name = "HourUTC"
			#{'Time': x_data, 'Value': y_data}
			return df

class ForecastDataProcessor(DataProcessor):
	@staticmethod
	def process_data(jsonData:dict)->pd.DataFrame:	
		if not jsonData:
			raise Exception("Error: Missing json data")
			return None
		else:
			parameter = list(jsonData['parameters'].keys())[0]
			timestamps = jsonData.get('domain', {}).get('axes', {}).get('t', {}).get('values', [])
			spliced_timestamps = [s[:13] for s in timestamps]
			values = jsonData.get('ranges', {}).get(parameter).get('values', [])
		if not timestamps and values:
			raise Exception("Error: Missing data for timestamps or values.")
			return None
		else:
			df = pd.DataFrame({parameter: values}, index=spliced_timestamps)
			df.index.name = "HourUTC"
			return df

class DataContainer:
	def __init__(self, url:str, payload:str, apiFetcher:ApiFetcher, dataProcessor:DataProcessor):
		self.url:str = url
		self.payload:dict = payload
		self.apiFetcher:ApiFetcher = apiFetcher
		self.dataProcessor:DataProcessor = dataProcessor
		self.df:pd.DataFrame=None

	def create_data(self):
		json_data = self.apiFetcher.fetch_data(self.url, self.payload)
		if json_data is None:
			print("No data available")
		else:
			self.df = self.dataProcessor.process_data(json_data)




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
	historical_forecasts = []
	for parameter in historical_parameters:
		payload={
				'parameter':parameter,
				'limit': 120,
				'resolution': 'hour',
				'time_from': (datetime.today()-timedelta(days=5)).isoformat()[:10],
				'time_to': datetime.today().isoformat()[:10]
				}
		historical_forecast_container = DataContainer(weather_url, payload, apiFetcher, historicalProcessor) 
		historical_forecast_container.create_data()
		historical_forecasts.append(historical_forecast_container)

	for forecast in historical_forecasts:
		print(forecast.payload['parameter'])	

	#forecast_url = 'http://127.0.0.1:8000/forecast'
	#coords = 'POINT(9.5 56.0)'
	#edr_parameters = [
	#					'relative-humidity-2m',  # mean_relative_hum
    #					'temperature-2m',        # mean_temp
    #					'wind-speed-10m',        # mean_wind_speed
    #					'pressure-surface',  # mean_pressure
    #					'direct-solar-exposure',       # mean_radiation
    #					'total-precipitation', # acc_precip
    #					'high-cloud-cover',
    #					'medium-cloud-cover',
    #					'low-cloud-cover'           # mean_cloud_cover
	#					]
	#forecasts = []
	#for parameter in edr_parameters:
	#	payload={
	#			'coords':coords,
	#			'crs':'crs84',
	#			'parameter':parameter
	#			}
	#	forecast_container = DataContainer(forecast_url, payload, apiFetcher,forecastProcessor)
	#	forecast_container.create_data()
	#	forecasts.append(forecast_container)
#
	#for forecast in forecasts:
	#	print(forecast.payload['parameter'])
		
							
if __name__ =='__main__':
	main()