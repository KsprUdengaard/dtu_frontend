import streamlit as st
import plotly.express as px
import requests
import pandas as pd
from datetime import datetime, timedelta
from utility_classes import *

# Function to plot the data
def plot_weather_data(df:pd.DataFrame, plot_type:str, y_axis_label:str, title:str)->None:
	plot_functions = {
		'line': px.line,
		'scatter': px.scatter,
		'bar': px.bar,
		'box': px.box,
		'histogram': px.histogram
	}

	if plot_type in plot_functions:
		fig = plot_functions[plot_type](df, title=title)
		fig.update_layout(yaxis_title=y_axis_label)
		st.plotly_chart(fig)
	else:
		st.error(f"Unsupported plot type: {plot_type}")


def show():
	### Variables ###
	weather_url = "http://127.0.0.1:8000/weather"
	resolutions = ['hour', 'day', 'month', 'year']	
	data_limit = 1000
	historical_parameters =  [
		"mean_relative_hum",
    	"mean_temp",
    	"mean_wind_speed", 
    	"mean_pressure",
    	"mean_radiation",
    	"acc_precip",
    	"mean_cloud_cover"
    ]
	
	### UI ###
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
	apiFetcher = ApiFetcher()
	historicalProcessor = HistoricalDataProcessor()
	data_transformer = Transformer()
	historical_forecasts = []
	if st.button('Request Data'):
		with st.spinner("Fetching historical data... Please wait."):
			for parameter in historical_parameters:
				payload={
						'parameter':parameter,
						'limit': data_limit,
						'resolution': resolution,
						'time_from': start_date,
						'time_to': end_date
						}
				container = DataContainer(weather_url, payload, apiFetcher, historicalProcessor, data_transformer) 
				container.create_data()
				historical_forecasts.append(container)
	
			with tab1:			
				st.header('Average humidity [%]')
				if historical_forecasts[0].df is None:
					st.write('Could not fetch data')
				else:
					plot_weather_data(historical_forecasts[0].df, plot_type='line',y_axis_label='Humidity [%]', title='Historical Average Humidity')
	
			with tab2:			
				st.header('Average temperature [°C]')
				if historical_forecasts[1].df is None:
					st.write('Could not fetch data')
				else:	
					plot_weather_data(historical_forecasts[1].df,plot_type='line',y_axis_label='Temperature [°C]', title='Historical Average Humidity')
	
			with tab3:			
				st.header('Average wind speed [m/s]')
				if historical_forecasts[2].df is None:
					st.write('Could not fetch data')
				else:
					plot_weather_data(historical_forecasts[2].df,plot_type='line',y_axis_label='Wind speed [m/s]', title='Historical Average Wind speed')
	
			with tab4:
				st.header('Average pressure [hPa]')
				if historical_forecasts[3].df is None:
					st.write('Could not fetch data')
				else:
					plot_weather_data(historical_forecasts[3].df,plot_type='line',y_axis_label='Pressure [hPa]', title='Historical Average Pressure')
			
			with tab5:
				st.header('Average radiation [W/m²]')
				if historical_forecasts[4].df is None:
					st.write('Could not fetch data')
				else:
					plot_weather_data(historical_forecasts[4].df,plot_type='line',y_axis_label='Radiation [W/m²]', title='Historical Average Radiation')
			
			with tab6:
				st.header('Accumulated precipitation [mm]')
				if historical_forecasts[5].df is None:
					st.write('Could not fetch data')
				else:
					plot_weather_data(historical_forecasts[5].df,plot_type='bar', y_axis_label='Precipitation [mm]', title='Historical Average Precipitation')
			
			with tab7:
				st.header('Average cloud cover [%]')
				if historical_forecasts[6].df is None:
					st.write('Could not fetch data')
				else:
					plot_weather_data(historical_forecasts[6].df,plot_type='line',y_axis_label='Cloud cover [%]', title='Historical Average Cloud cover')