import streamlit as st
import json
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
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
gcod_df_df = gcod_df
gcod_df_df['startdatetime'] = pd.to_datetime(gcod_df_df['properties.starttime'])
gcod_df_df['year'] = gcod_df_df['startdatetime'].dt.year
gcod_df_df['month'] = gcod_df_df['startdatetime'].dt.month
gcod_df_df['date'] = gcod_df_df['startdatetime'].dt.date
gcod_df_df['hour'] = gcod_df_df['startdatetime'].dt.hour
gcod_df_df['minute'] = gcod_df_df['startdatetime'].dt.minute
####### for end time conversion
gcod_df_df['enddatetime'] = pd.to_datetime(gcod_df_df['properties.endtime'])
gcod_df_df['endyear'] = gcod_df_df['enddatetime'].dt.year
gcod_df_df['endmonth'] = gcod_df_df['enddatetime'].dt.month
gcod_df_df['enddate'] = gcod_df_df['enddatetime'].dt.date
gcod_df_df['endhour'] = gcod_df_df['enddatetime'].dt.hour
gcod_df_df['endminute'] = gcod_df_df['enddatetime'].dt.minute
gcod_group_trip = df
gcod_group_trip = gcod_group_trip.groupby(['properties.taxiid'])['properties.taxiid'].count()
gcod_group_trip_top = gcod_group_trip.nlargest(30)

# Explore for Street names ############
gcod_street_df = df.explode('properties.streetnames')
# Remove column name 'geometry.coordinates'
gcod_street_df = gcod_street_df.drop(['geometry.coordinates'], axis=1)
# Count unique street name
total_no_street = gcod_street_df['properties.streetnames'].nunique()

# Calculate most engageed streat and add new column
#gcod_street_df= gcod_street_df['properties.streetnames'].value_counts(normalize=True)
top_engaged_street_df = gcod_street_df['properties.streetnames'].value_counts().rename_axis('street').reset_index(name='counts')
top_ten_street = top_engaged_street_df.nlargest(10, 'counts').set_index('street')

top_speed_df = gcod_street_df['properties.maxspeed'].value_counts().rename_axis('Top Speed').reset_index(name='counts')
top_ten_speed = top_speed_df.nlargest(10, 'counts')

# Layout and design for data visualization
st.header("Traffic Analysis")
tab_dashboard, tab_raw = st.tabs(["Dashboard", "Raw Data"])
with st.container():
    #with st.sidebar:
        #st.subheader("Metrix")

    with tab_dashboard:
        st.subheader("Summary:")
        col_taxis, col_trips, col_street = st.columns(3)
        with col_taxis:
            st.write("Total Number of Taxis")
            st.success(total_no_taxis)

        with col_trips:
            st.write("Total Trips")
            st.success(total_no_trips)

        with col_street:
            st.write("Total number of Street Engaged")
            st.success(total_no_street)

        st.subheader("Traffic On Map:")
        st.map(gcod_df[['lon','lat']], zoom=11, )

        col_dist_ave_speed, col_top_ten, col_pichart = st.columns([1.5, 1.3, 3])
        with col_dist_ave_speed:
            st.write("Ave.Speeed vs Max.Speed vs Distance vs Duration:")
            df2 = df
            df2 = pd.DataFrame(df2, columns=['properties.tripid', 'properties.avspeed', 'properties.maxspeed', 'properties.duration'])
            df2.rename(columns = {'properties.tripid':'Trip Id', 'properties.avspeed':'Average Speed', 'properties.maxspeed':'Max Speed', 'properties.duration': 'Duration'}, inplace = True)
            df2 = df2.round(decimals = 2).set_index('Trip Id').nlargest(100, ['Average Speed'])
            st.write(df2)

        with col_top_ten:
            st.write("Top 10 Busy Road:")
            st.write(top_ten_street)

        with col_pichart:
            st.write("Road Engagement:")
            st.bar_chart(top_ten_street)

        col_box_plot, col_line_chart = st.columns(2)
        with col_line_chart:
            st.write("Ave.Speeed vs Max.Speed vs Distance vs Duration top 100 records:")
            df3 = df2.nlargest(100, ['Average Speed'])
            st.line_chart(df3)

        with col_box_plot:
            st.write("Trips with Time:")
            fig = px.box(gcod_df_df, x="hour", y="properties.tripid")
            # Plot
            st.plotly_chart(fig, use_container_width=True)
        
        col_max_speed, col_min_speed, col_ave_speed = st.columns(3)
        with col_max_speed:
            fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = df['properties.maxspeed'].max(),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Top Speed in Max. Column"}))
            st.plotly_chart(fig, use_container_width=True)

        with col_min_speed:
            fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = df['properties.minspeed'].max(),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Top Speed in Min. Column"}))
            st.plotly_chart(fig, use_container_width=True)

        with col_ave_speed:
            fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = df['properties.avspeed'].max(),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Top Speed in Avg. Column"}))
            st.plotly_chart(fig, use_container_width=True)

        st.write(gcod_group_trip_top)

    with tab_raw:
        st.subheader("Raw Data")
        st.dataframe(df)
        st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='raw.csv',
        mime='text/csv',
        )