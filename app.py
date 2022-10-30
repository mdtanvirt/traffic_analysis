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

# Explore for Street names ############
gcod_street_df = df.explode('properties.streetnames')
# Remove column name 'geometry.coordinates'
gcod_street_df = gcod_street_df.drop(['geometry.coordinates'], axis=1)
# Count unique street name
total_no_street = gcod_street_df['properties.streetnames'].nunique()

# Calculate most engageed streat and add new column
#gcod_street_df= gcod_street_df['properties.streetnames'].value_counts(normalize=True)
top_engaged_street_df = gcod_street_df['properties.streetnames'].value_counts().rename_axis('street').reset_index(name='counts')
top_ten_street = top_engaged_street_df.nlargest(10, 'counts')

# Layout and design for data visualization
tab_dashboard, tab_map, tab_raw = st.tabs(["Dashboard", "Map", "Raw Data"])
with st.container():
    with tab_dashboard:
        with st.sidebar:
            nav_menu = option_menu("Main Menu", ["Dashboard", "Map", 'Raw Data'],
                icons=['clipboard-data', 'map', 'gear'], menu_icon="cast", default_index=0)
        col_taxis, col_trips, col_street = st.columns(3)
        col_taxis.metric("Total", total_no_taxis)
        col_trips.metric("Total", total_no_trips)
        col_street.metric("Total", total_no_street)

    with tab_map:
        st.text("Map Analysis")
        st.map(gcod_df[['lon','lat']], zoom=11)
        st.text("Top 10 Busy Road")
        st.write(top_ten_street['street'])
        st.area_chart(top_ten_street)

    with tab_raw:
        st.title("Raw Data")
        st.dataframe(df)
        st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='raw.csv',
        mime='text/csv',
        )