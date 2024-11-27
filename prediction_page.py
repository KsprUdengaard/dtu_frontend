import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utility_classes import *

def plot_data(history_df:pd.DataFrame, forecast_df:pd.DataFrame, plot_type:str, y_axis_label:str, title:str):
	plot_functions = {
		'line': px.line,
		'scatter': px.scatter,
		'bar': px.bar,
		'box': px.box,
		'histogram': px.histogram
	}
	if history_df is None or forecast_df is None:
		st.write(f"Missing either historical- or forecast data for **{title}**")
	else:
		history_df["Source"] = "Historical"
		forecast_df["Source"] = "Future"
		combined_df = pd.concat([history_df, forecast_df])
		if plot_type in plot_functions:
			fig = plot_functions[plot_type](
				combined_df,
				color="Source", 
				title=title)	
			fig.update_layout(yaxis_title=y_axis_label)
			st.plotly_chart(fig)
		else:
			st.error(f"Unsupported plot type: {plot_type}")

def show():

	st.title("Forecast")
	st.write('This forecast show weather and energy spot prices from the past five days and forcast for the coming two days')
	st.markdown("---")
		### Variables ###
	apiFetcher = ApiFetcher()
	historicalProcessor = HistoricalDataProcessor()
	forecastProcessor = ForecastDataProcessor()
	data_transformer = Transformer()
	weather_url = "http://127.0.0.1:8000/weather"
	resolutions = ['hour', 'day', 'month', 'year']	
	data_limit = 1000
	forecast_url = 'http://127.0.0.1:8000/forecast'
	coords = 'POINT(9.5 56.0)'
	historical_parameters = [
   		{"header": "Average humidity [%]", "parameter": "mean_relative_hum",'edr_parameter':'relative-humidity-2m', "y_axis_label": "Humidity [%]", "plot_type": "line"},
   		{"header": "Average temperature [°C]", "parameter": "mean_temp",'edr_parameter':'temperature-2m', "y_axis_label": "Temperature [°C]", "plot_type": "line"},
   		{"header": "Average wind speed [m/s]", "parameter": "mean_wind_speed",'edr_parameter':'wind-speed-10m', "y_axis_label": "Wind speed [m/s]", "plot_type": "line"},
   		{"header": "Average pressure [hPa]", "parameter": "mean_pressure",'edr_parameter':'pressure-surface', "y_axis_label":'pressure-surface' "Pressure [hPa]", "plot_type": "line"},
   		{"header": "Average radiation [W/m²]", "parameter": "mean_radiation",'edr_parameter':'global-radiation-flux',"y_axis_label": "Radiation [W/m²]", "plot_type": "line"},
   		{"header": "Accumulated precipitation [mm]", "parameter": "acc_precip",'edr_parameter':'total-precipitation', "y_axis_label": "Precipitation [mm]", "plot_type": "bar"},
   		{"header": "Average cloud cover [%]","parameter": "mean_cloud_cover",'edr_parameter':'',"y_axis_label": "Cloud cover [%]","plot_type": "line"}
	]
	historical_forecasts = []
	predictive_forecasts=[]
	for parameter in historical_parameters:
		with st.spinner(f'Fetching {parameter['header']} data'):
			historical_payload={
					'parameter':parameter['parameter'],
					'limit': 120,
					'resolution': 'hour',
					'time_from': (datetime.today()-timedelta(days=5)).isoformat()[:10],
					'time_to': datetime.today().isoformat()[:10]
					}
			historical_forecast_container = DataContainer(url=weather_url, 
														payload=historical_payload, 
														apiFetcher=apiFetcher, 
														dataProcessor=historicalProcessor, 
														transformer=data_transformer) 
			historical_forecast_container.create_data()
			historical_forecasts.append(historical_forecast_container)
			if parameter['parameter']=='mean_cloud_cover':
				pass
			else:
				forecaste_payload={
						'coords':coords,
						'crs':'crs84',
						'parameter':parameter['edr_parameter']
						}
				forecast_container = DataContainer(url=forecast_url, 
										payload=forecaste_payload, 
										apiFetcher=apiFetcher,
										dataProcessor=forecastProcessor,
										transformer=data_transformer)
				forecast_container.create_data()
				predictive_forecasts.append(forecast_container)

	with st.spinner(f'Fetching {parameter['header']} data'):
		cloud_cover_parameters = ['high-cloud-cover','medium-cloud-cover','low-cloud-cover']
		cloud_data_dataframes=[]
		for parameter in cloud_cover_parameters:
			cloud_payload={'coords':coords,'crs':'crs84','parameter':parameter}
			data = apiFetcher.fetch_data(forecast_url, cloud_payload)
			processed_data=forecastProcessor.process_data(data, data_transformer)
			processed_data = processed_data.rename(columns={parameter: 'value'})
			cloud_data_dataframes.append(processed_data)
		
		mean_cloud_cover = sum(cloud_data_dataframes)/len(cloud_data_dataframes)
		mean_cloud_cover = mean_cloud_cover.rename(columns={'value': 'mean_cloud_cover'})
		cloud_container = DataContainer()
		cloud_container.df = round(mean_cloud_cover, 1)
		predictive_forecasts.append(cloud_container)
		
	### UI ###
	
	for i, parameter in enumerate(historical_parameters):
		if historical_forecasts[i].df is None or predictive_forecasts[i].df is None:
			st.markdown("---")
			st.write(f'Could not fetch **{parameter['header']}** data')
			pass
		else:
			plot_data(history_df=historical_forecasts[i].df, 
					  forecast_df=predictive_forecasts[i].df,
					  plot_type=parameter['plot_type'],
					  y_axis_label=parameter['y_axis_label'],
					  title=parameter['header'])

	st.write('Energy spot price forecast!')		