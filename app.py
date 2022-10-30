import streamlit as st
import json
import pandas as pd
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

# Hide streamlit default menu and footer from the template
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden}
    footer {visibility: hidden}
    header {visibility: hidden}
    div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Read JSON file
with open('trips.json', 'r') as f:
    data = json.loads(f.read())

# Normalize data
df = pd.json_normalize(data, record_path =['features'])

# Count distinct values from taxi id column
total_no_taxis = df['properties.taxiid'].nunique()

# Count distinct values from trip id column
total_no_trips = df['properties.tripid'].nunique()

# Layout and design for data visualization
with st.sidebar:
    nav_menu = option_menu("Main Menu", ["Dashboard", "Map", 'Raw Data'],
        icons=['clipboard-data', 'map', 'gear'], menu_icon="cast", default_index=0)

if nav_menu == "Dashboard":
    st.header("Analysis Dashboard")
    st.text("Total number of Taxis")
    st.text(total_no_taxis)
    st.text("Total number of Trips")
    st.text(total_no_trips)