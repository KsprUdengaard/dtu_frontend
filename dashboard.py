import streamlit as st
from webpages.energy_page import *
from webpages.weather_page import *
from webpages.landing_page import *
from webpages.prediction_page import *
from webpages.about_page import *

class App:
    @staticmethod
    def render():
        tabs = st.tabs(['Home','Energy data','Weather data', 'Predictions', 'About'])

        with tabs[0]:
            LandingPage.render()
        with tabs[1]:
            EnergyPage.render()
        with tabs[2]:
            WeatherPage.render()
        with tabs[3]:
            PredictionPage.render()
        with tabs[4]:
            AboutPage.render()
        

def main():
    App.render()

if __name__ == "__main__":
    main()
