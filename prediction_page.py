import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utility_classes import *

def plot_data(weather_data:dict, forecast_data:dict, plot_type:str, y_axis_label:str, title:str):
	plot_functions = {
		'line': px.line,
		'scatter': px.scatter,
		'bar': px.bar,
		'box': px.box,
		'histogram': px.histogram
	}

	weather_df = pd.DataFrame(weather_data)
	weather_df["Source"] = "Historical"
	forecast_df = pd.DataFrame(forecast_data)
	forecast_df["Source"] = "Future"
	combined_df = pd.concat([weather_df, forecast_df])

	if plot_type in plot_functions:
		fig = plot_functions[plot_type](
			combined_df,
			x="timestamps",
			y="values",
			color="Source", 
			title=title,
			labels={'timestamps':'Time (UTC)',
					'values':y_axis_label,
					'source':'Data Type'
					})	
		st.plotly_chart(fig)
	else:
		st.error(f"Unsupported plot type: {plot_type}")

def show():
	st.title("Forecast")
	st.write('This forecast show weather and energy spot prices from the past five days and forcast for the coming two days')
	st.markdown("---")
	st.write('Forecast')
		### Variables ###
	weather_url = "http://127.0.0.1:8000/weather"
	resolutions = 'hour'	
	data_limit = 120
	forecast_url = 'http://127.0.0.1:8000/forecast'
	coords = 'POINT(9.5 56.0)'
	tab_data = [
   		{"title": "Humidity", "parameter": "mean_relative_hum",'edr_parameter':'relative-humidity-2m', "y_axis_label": "Humidity [%]", "plot_type": "line"},
   		{"title": "Temperature", "parameter": "mean_temp",'edr_parameter':'temperature-2m', "y_axis_label": "Temperature [°C]", "plot_type": "line"},
   		{"title": "Wind speed", "parameter": "mean_wind_speed",'edr_parameter':'wind-speed-10m', "y_axis_label": "Wind speed [m/s]", "plot_type": "line"},
   		{"title": "Pressure ", "parameter": "mean_pressure",'edr_parameter':'pressure-surface', "y_axis_label": "Pressure [hPa]", "plot_type": "line"},
   		{"title": "Radiation", "parameter": "mean_radiation",'edr_parameter':'global-radiation-flux',"y_axis_label": "Radiation [W/m²]", "plot_type": "line"},
   		{"title": "Acc precipitation", "parameter": "acc_precip",'edr_parameter':'total-precipitation', "y_axis_label": "Precipitation [mm]", "plot_type": "bar"},
   		{"title": "Cloud cover","parameter": "mean_cloud_cover",'edr_parameter':'',"y_axis_label": "Cloud cover [%]","plot_type": "line"}
	]

	tabs =st.tabs([tab['title'] for tab in tab_data])

	weather_payloads = {'items':[]}
	forecast_payloads = {'items':[]}
	
	#with st.spinner(f'Fetching {tab['title']} data'):
	for tab in tab_data:	
		if tab['parameter']=='mean_cloud_cover':
			pass
		else:
			historical_payload={
					'parameter':tab['parameter'],
					'limit': data_limit,
					'resolution': 'hour',
					'time_from': (datetime.today()-timedelta(days=5)).isoformat()[:10],
					'time_to': datetime.today().isoformat()[:10]
					}
			weather_payloads['items'].append(historical_payload)
			forecast_payload={
					'coords':coords,
					'crs':'crs84',
					'parameter':tab['edr_parameter']
					}
		forecast_payloads['items'].append(forecast_payload)
	weather_data = ApiFetcher.fetch_data(weather_url, weather_payloads)
	forecast_data = ApiFetcher.fetch_data(forecast_url, forecast_payloads)
	for idx, tab in enumerate(tabs):
		with tab:
			if 'Server Error' in forecast_data:
				st.write('Cannot plot data due to forecast data timeout - try and refresh')
			else:
				if tab_data[idx]['parameter'] =='mean_cloud_cover':
					cloud_payload={
								'parameter':tab_data[idx]['parameter'],
								'limit': data_limit,
								'resolution': 'hour',
								'time_from': (datetime.today()-timedelta(days=5)).isoformat()[:10],
								'time_to': datetime.today().isoformat()[:10]
								}
					cloud_data = ApiFetcher.fetch_data(weather_url, cloud_payload)
					cloud_forecast_list = ['high-cloud-cover','medium-cloud-cover','low-cloud-cover']
					cloud_forecast_payloads = {'items':[]}
					for cloud_parameter in cloud_forecast_list:
						cloud_payload={
								'coords':coords,
								'crs':'crs84',
								'parameter':cloud_parameter
								}
						cloud_forecast_payloads['items'].append(cloud_payload)
					cloud_forecast_data = ApiFetcher.fetch_data(forecast_url, cloud_forecast_payloads)
					value_list1 = cloud_forecast_data['results'][0]['values']
					value_list2 = cloud_forecast_data['results'][1]['values']
					value_list3 = cloud_forecast_data['results'][2]['values']
					averaged_list = [round((x + y + z) / 3, 1) for x, y, z in zip(value_list1, value_list2, value_list3)]
					average_forecast_cloud_data = {'timestamps':cloud_forecast_data['results'][0]['timestamps'], 'values':averaged_list}
					plot_data(weather_data=cloud_data,
							  forecast_data=average_forecast_cloud_data,
							  plot_type=tab_data[idx]['plot_type'],
							  y_axis_label=tab_data[idx]['y_axis_label'],
							  title=tab_data[idx]['title'])
				else:
					plot_data(weather_data={'timestamps':weather_data['results'][idx]['timestamps'], 'values':weather_data['results'][idx]['values']},
							  forecast_data={'timestamps':forecast_data['results'][idx]['timestamps'], 'values':forecast_data['results'][idx]['values']},
							  plot_type=tab_data[idx]['plot_type'],
							  y_axis_label=tab_data[idx]['y_axis_label'],
							  title=tab_data[idx]['title'])