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
		except requests.exceptions.RequestException as http_err:
			return {
				"error": f"HTTP error occurred: {http_err}",
				"status_code": http_err.response.status_code
				}
		except requests.exceptions.RequestException as e:
			return {
				"error": f"API fetch error: {e}",
				"status_code": 500  # Default code for non-HTTP errors
				}


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