import streamlit as st
import pandas as pd
import plotly.express as px

def plot_forecast_data(df, plot_type, y_axis_label, title):
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
	st.title("Forecast")

	st.write('This forecast show weather and energy spot prices from the past five days and forcast for the comming two days')
	
	tab1, tab2, tab3 = st.columns(3)

	with tab1:
		st.write('Humidity')
		st.write('Temperature')
		
	with tab2:
		st.write('Wind speed')
		st.write('Pressure')

	with tab3:
		st.write('Solar radiation')
		st.write('Precipitation')
		st.write('Cloud cover')	

	st.write('Energy spot price forecast!')