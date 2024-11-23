import streamlit as st

def show():
	st.title("Energy Data")
	st.write("This page displays energy consumption data.")
	st.write("You can display charts or data trends related to energy usage.")
	search_query = st.text_input("Search for something:", placeholder="Type your query here...")
	