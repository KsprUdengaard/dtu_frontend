import streamlit as st
import plotly.express as px
import requests
import pandas as pd
from datetime import datetime

class call_for_plot:
	def __init__ (self):
		pass

def show():
	st.title('Weather Data')
	
	### Variables ###
	tabs = ['Humidity', 
			'Temp',  
			'Wind speed', 
			'Wind direction', 
			'Pressure', 
			'Radiation',
			'Precipitation',
			'Cloud cover',
			'Soil temperature']

	weather_url = "http://127.0.0.1:8000/weather"
	resolutions = ['hour', 'day', 'month', 'year']
	tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(tabs)

	### Interface ###
	with tab1:
		humidity_parameter = 'mean_relative_hum'
		st.header('Average humidity [%]')
		hum_col1, hum_col2, hum_col3 = st.columns(3)
		with hum_col1:
			start_date = st.date_input('Start Date', datetime.today(), min_value=datetime(2000, 1, 1)).isoformat()
		with hum_col2:
			end_date = st.date_input('End Date', datetime.today(), min_value=datetime(2000, 1, 1)).isoformat()
		with hum_col3:
			resolution = st.selectbox('Choose a resolution', resolutions)
		hummidity_limit = st.slider('Data limit', min_value=10, max_value=1000, step=5)


		if st.button('Request Data'):
			if start_date > end_date:
				st.error('Start date must be before end date')
			elif start_date > datetime.today().isoformat() or end_date > datetime.today().isoformat():
				st.error('Dates cannot exceed current date')
			else:
				hum_payload = {'parameter':humidity_parameter, 
								'limit':hummidity_limit, 
								'resolution':resolution, 
								'time_from':start_date,
								'time_to':end_date}
				response = requests.post(weather_url, json=hum_payload)
				if response.status_code == 200:
					
					hum_data = response.json()['data']['features']
					x_data = [feature['properties']['from'][:13] for feature in hum_data]
					y_data = [feature['properties']['value'] for feature in hum_data]
					hum_df = pd.DataFrame({
						'Date':x_data,
						'Humidity [%]':y_data
						})
					fig = px.line(hum_df, x='Date', y='Humidity [%]', title='Historical average humidity data')
					st.plotly_chart(fig)
					st.success('Request sent succesfully!')
	
				else:
					st.error(f'Failed to send request, Status code {response.status_code}')


	with tab2:
		st.header('Average temperature [°C]')
	with tab3:
		st.header('Average wind speed [m/s]')
	with tab4:
		st.header('Average wind direction [degrees]')
	with tab5:
		st.header('Average pressure [hPa]')
	with tab6:
		st.header('Average radiation [MJ/m²]')
	with tab7:
		st.header('Accumulated precipitation [mm]')
	with tab8:
		st.header('Average cloud cover [%]')
	with tab9:
		st.header('Average temperature in 10 cm soil [°C]')