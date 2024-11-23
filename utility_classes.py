import pandas as pd
import requests
from datetime import datetime, timedelta

class DMI_Forecast:
	def __init__(self, coords: str, parameter: str):
			self.coords = coords
			self.parameter = parameter
			self.json_data = None
			self.forecast_df = None

	def fetch_data(self, forecast_url:str)->None:
		payload = {
			'coords': self.coords,
			'crs': 'crs84',
			'parameter': self.parameter,
		}

		response = requests.get(forecast_url, json=payload)
		if response.status_code != 200:
			raise Exception(f"Error: {response.status_code} - {response.text}")
		self.json_data = response.json()

	def process_data(self, unit:str)->pd.DataFrame:
		timestamps = self.json_data.get('domain', {}).get('axes', {}).get('t', {}).get('values', [])
		values = self.json_data.get('ranges', {}).get(self.parameter, {}).get('values', [])

		# Return as DataFrame if both timestamps and values exist
		if timestamps and values:
			self.forecast_df = pd.DataFrame({self.parameter: values}, index=timestamps)
			self.forecast_df[self.parameter] = self.forecast_df[self.parameter].apply(self.conversion_lambda)
			self.forecast_df.index.name = "HourUTC"
			self.forecast_df.columns = [f'{self.parameter} - {unit}']
			return self.forecast_df
		else:
			raise Exception("Error: Missing data for timestamps or values.")

class DMI_Historical_data:
	def __init__(self, parameter:str, start_date:str, end_date:str, data_limit:int):
		self.start_date=start_date
		self.end_date=end_date
		self.data_limit=data_limit
		self.resolution="hour"
		self.parameter=parameter
		self.json_data = None
		self.historical_df = None

	def fetch_weather_data(self, weather_url:str)->None:
		payload = {
			'parameter': self.parameter,
			'limit': self.data_limit,
			'resolution': self.resolution,
			'time_from': self.start_date,
			'time_to': self.end_date
		}
		response = requests.post(weather_url, json=payload)
		if response.status_code != 200:
			print(response.text)
			#st.error(f'Failed to send request, Status code {response.status_code}')
			return None	
		else:
			self.json_data = response.json()

	def process_data(self)->pd.DataFrame:
		if not self.json_data:
			print('No data available') 
		else:
			x_data = [feature['properties']['from'][:13] for feature in self.json_data]
			y_data = [feature['properties']['value'] for feature in self.json_data]
			self.historical_df = pd.DataFrame({'Time': x_data, 'Value': y_data})
			return self.historical_df

def main()->None:
	start_date = (datetime.today()-timedelta(days=5)).isoformat()[:10]
	end_date = datetime.today().isoformat()[:10]
	weather_url = "http://127.0.0.1:8000/weather"
	parameter = 'mean_pressure'
	hist_data = DMI_Historical_data(parameter, start_date, end_date, 120)
	hist_data.fetch_weather_data(weather_url)
	hist_data.process_data()
	print(hist_data.historical_df)

if __name__ =='__main__':
	main()