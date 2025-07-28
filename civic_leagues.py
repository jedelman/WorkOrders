import streamlit as st
import pydeck as pdk
import pydeck.data_utils as du
import geopandas as gpd

civicleagues = gpd.read_file('Civic_Leagues.geojson')

color_dict = du.assign_random_colors(civicleagues['LEAGUE'])

viewstate = pdk.ViewState(latitude=36.8508, longitude=-76.2859, zoom=10, pitch=45, bearing=10)

# Define a layer to display on a map
layer = pdk.Layer(
    'GeoJsonLayer',
    civicleagues,
    opacity=0.2,
    stroked=True,
    auto_highlight=True,
    filled=True,
    wireframe=True,
    elevation_scale=5,
    pickable=True,
    get_fill_color='[0, 255, 122]',
    elevation_range=[0, 3000],
    extruded=False,
    coverage=1)

deck = pdk.Deck(layer, initial_view_state=viewstate)

st.pydeck_chart(deck)