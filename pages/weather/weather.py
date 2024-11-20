import streamlit as st
import plotly.express as px
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_weather_data(parameter, start_date, end_date, resolution, data_limit, weather_url):
	if start_date > end_date:
		st.error('Start date must be before end date')
		return None
	elif start_date > datetime.today().isoformat() or end_date > datetime.today().isoformat():
		st.error('Dates cannot exceed the current date')
		return None

	payload = {
		'parameter': parameter,
		'limit': data_limit,
		'resolution': resolution,
		'time_from': start_date,
		'time_to': end_date,
	}

	response = requests.post(weather_url, json=payload)
	if response.status_code == 200:
		# Extract data from the response
		data = response.json()['data']['features']
		x_data = [feature['properties']['from'][:13] for feature in data]
		y_data = [feature['properties']['value'] for feature in data]
		df = pd.DataFrame({'Time': x_data, 'Value': y_data})
		return df
	else:
		st.error(f'Failed to send request, Status code {response.status_code}')
		return None

# Function to plot the data
def plot_weather_data(df, plot_type, y_axis_label, title):
	plot_functions = {
		'line': px.line,
		'scatter': px.scatter,
		'bar': px.bar,
		'box': px.box,
		'histogram': px.histogram
	}

	if plot_type in plot_functions:
		fig = plot_functions[plot_type](df, x='Time', y='Value', title=title)
		fig.update_layout(yaxis_title=y_axis_label)
		st.plotly_chart(fig)
	else:
		st.error(f"Unsupported plot type: {plot_type}")


def show():

	### Variables ###
	weather_url = "http://127.0.0.1:8000/weather"
	resolutions = ['hour', 'day', 'month', 'year']	
	data_limit = 1000
	st.title('Weather Data')
	
	col1, col2, col3 = st.columns(3)
	with col1:
		start_date = st.date_input('From Date', datetime.today()-timedelta(days=1), min_value=datetime(2000, 1, 1)).isoformat()
	with col2:
		end_date = st.date_input('To Date', datetime.today(), min_value=datetime(2000, 1, 1)).isoformat()
	with col3:
		resolution = st.selectbox('Choose a resolution', resolutions)
	

	st.write('<small>*The maximum number of data points that can be requested is limited to 1,000</small>', unsafe_allow_html=True)
	
	
	tabs = ['Humidity', 
			'Temperature',  
			'Wind speed', 
			'Pressure', 
			'Radiation',
			'Precipitation',
			'Cloud cover']

	tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tabs)

	### Interface ###

	if st.button('Request Data'):
		with tab1:			
			st.header('Average humidity [%]')
			hum_parameter = 'mean_relative_hum'
			df = fetch_weather_data(
				parameter=hum_parameter,
				start_date=start_date,
				end_date=end_date,
				resolution=resolution,
				data_limit=data_limit,
				weather_url=weather_url)
			if df is not None:
				plot_weather_data(df,plot_type='line',y_axis_label='Humidity [%]', title='Historical Average Humidity')
		
		with tab2:			
			st.header('Average temperature [°C]')
			temp_parameter = 'mean_temp'
			df = fetch_weather_data(
				parameter=temp_parameter,
				start_date=start_date,
				end_date=end_date,
				resolution=resolution,
				data_limit=data_limit,
				weather_url=weather_url)
			if df is not None:
				plot_weather_data(df,plot_type='line',y_axis_label='Temperature [°C]', title='Historical Average Temperature')

		with tab3:			
			st.header('Average wind speed [m/s]')
			wind_speed_parameter = 'mean_wind_speed'
			df = fetch_weather_data(
				parameter=wind_speed_parameter,
				start_date=start_date,
				end_date=end_date,
				resolution=resolution,
				data_limit=data_limit,
				weather_url=weather_url)
			if df is not None:
				plot_weather_data(df,plot_type='line',y_axis_label='Wind speed [m/s]', title='Historical Average Wind speed')

		with tab4:
			st.header('Average pressure [hPa]')
			pressure_parameter = 'mean_pressure'
			df = fetch_weather_data(
				parameter=pressure_parameter,
				start_date=start_date,
				end_date=end_date,
				resolution=resolution,
				data_limit=data_limit,
				weather_url=weather_url)
			if df is not None:
				plot_weather_data(df,plot_type='line',y_axis_label='Pressure [hPa]', title='Historical Average Pressure')

		with tab5:
			st.header('Average radiation [MJ/m²]')
			radiation_parameter = 'mean_radiation'
			df = fetch_weather_data(
				parameter=radiation_parameter,
				start_date=start_date,
				end_date=end_date,
				resolution=resolution,
				data_limit=data_limit,
				weather_url=weather_url)
			if df is not None:
				plot_weather_data(df,plot_type='line',y_axis_label='Radiation [MJ/m²]', title='Historical Average Radiation')

		with tab6:
			st.header('Accumulated precipitation [mm]')
			precipitation_parameter = 'acc_precip'
			df = fetch_weather_data(
				parameter=precipitation_parameter,
				start_date=start_date,
				end_date=end_date,
				resolution=resolution,
				data_limit=data_limit,
				weather_url=weather_url)
			if df is not None:
				plot_weather_data(df,plot_type='bar',y_axis_label='Precipitation [mm]', title='Historical Average Precipitation')

		with tab7:
			st.header('Average cloud cover [%]')
			cloud_parameter = 'mean_cloud_cover'
			df = fetch_weather_data(
				parameter=cloud_parameter,
				start_date=start_date,
				end_date=end_date,
				resolution=resolution,
				data_limit=data_limit,
				weather_url=weather_url)
			if df is not None:
				plot_weather_data(df,plot_type='line',y_axis_label='Cloud cover [%]', title='Historical Average Cloud cover')

		