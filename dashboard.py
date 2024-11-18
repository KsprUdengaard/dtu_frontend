import streamlit as st

# Title of the app
st.title("Streamlit App Example")

# Display some text
st.write("This is a simple Streamlit app.")

# Create an input form
name = st.text_input("Enter your name:")
age = st.number_input("Enter your age:", min_value=0, max_value=120)

if st.button("Submit"):
    st.write(f"Hello {name}, you are {age} years old!")