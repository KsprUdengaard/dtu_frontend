import streamlit as st
import requests
import pages.about.about as about_page
import pages.weather.weather as weather_page
import pages.energy.energy as energy_page
import pages.prediction.prediction as prediction_page

def footer(message):
    return st.markdown(f"""
                        <style>
                            .footer {{
                                position: fixed;
                                bottom: 0;
                                left: 0;
                                width: 100%;
                                background-color: #f1f1f1;
                                text-align: center;
                                padding: 10px;
                                font-size: 14px;
                                color: #555;
                                border-top: 1px solid #ddd;
                            }}
                        </style>
                        <div class="footer">
                            <p>{message}</p>    
                        </div>
                        """, unsafe_allow_html=True)


def main()->None:
    ### Navigation in the sidebar ###
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["About", "Weather Data", "Energy Data", "Price prediction"])
    
    if page == "About":
        about_page.show()
    elif page == "Weather Data":
        weather_page.show()
    elif page == "Energy Data":
        energy_page.show()
    elif page == "Price prediction":
        prediction_page.show()

    ### Footer ###
    api_url = "http://127.0.0.1:8000"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json() 
            footer(data['message'])
        else:
            data = response.json()
            footer(data['message'])
    except requests.exceptions.RequestException as e:
        footer(f'Lost connection to API')


if __name__ == "__main__":
    main()