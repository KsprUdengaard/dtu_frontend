import streamlit as st

class PredictionPage:
    @staticmethod
    def render():
        st.title("Price Prediction")
        st.write("This page contains price prediction models.")
        st.write("Here, you can show the results of energy price predictions based on historical data.")
