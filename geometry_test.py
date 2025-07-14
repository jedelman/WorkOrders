import geopandas as gpd
import streamlit as st
import altair as alt
import pyarrow as pa

result = st.container()

civic_leagues = "https://gisshare.norfolk.gov/pubserver/rest/services/OpenData/Maps/FeatureServer/12/query?outFields=*&where=1%3D1&f=geojson"

geodata = gpd.read_file(civic_leagues, bbox=None)

geochart = alt.Chart(geodata).mark_geoshape()

geochart = geochart.encode(color='LEAGUE:N')

with result:
    st.write(geochart)
