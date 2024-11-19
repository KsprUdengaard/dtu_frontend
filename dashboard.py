import streamlit as st
import pages.about.about as about_page
import pages.weather.weather as weather_page
import pages.energy.energy as energy_page
import pages.prediction.prediction as prediction_page


def main()->None:
    # Navigation in the sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["About", "Weather Data", "Energy Data", "Price prediction"])
    
    # Show the selected page
    if page == "About":
        about_page.show()
    elif page == "Weather Data":
        weather_page.show()
    elif page == "Energy Data":
        energy_page.show()
    elif page == "Price prediction":
        prediction_page.show()

if __name__ == "__main__":
    main()
