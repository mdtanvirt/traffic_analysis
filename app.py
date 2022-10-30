import streamlit as st
import json
import pandas as pd
import pydeck as pdk
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

# Convert to csv for download button
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(df)

# Count distinct values from taxi id column
total_no_taxis = df['properties.taxiid'].nunique()

# Count distinct values from trip id column
total_no_trips = df['properties.tripid'].nunique()

# Explore coordinate with lat lng from data set
## Explore for coordinates
gcod_df = df.explode('geometry.coordinates')
## Remove column name 'properties.streetnames'
gcod_df = gcod_df.drop(['properties.streetnames'], axis=1)
gcod_df[['lon','lat']] = pd.DataFrame(gcod_df["geometry.coordinates"].tolist(), index= gcod_df.index)

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

    

if nav_menu == "Map":
    st.header("Analysis with Map")
    st.map(gcod_df[['lon','lat']], zoom=11)

if nav_menu == "Raw Data":
    st.header("Raw data")
    st.dataframe(df)
    st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='raw.csv',
    mime='text/csv',
    )