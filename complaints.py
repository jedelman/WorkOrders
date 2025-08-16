import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pydeck.data_utils as du
import altair as alt
from shapely.geometry import Point
import db
import re

st.set_page_config(layout='wide')

civicleagues = gpd.read_file('Civic_Leagues.geojson')

selected_civic_league = civicleagues.query(f'LEAGUE == "{st.session_state.get("selected_civic_league", "Ghent Neighborhood League")}"')

complaints = gpd.GeoDataFrame(db.get_complaints_from_local_db())

mnf = db.get_mnf()

mnf = mnf.clip(selected_civic_league.geometry)

# mnf = mnf.clip(selected_civic_league.geometry)                           

f"""
# requests

{len(mnf)}

"""

complaints = complaints.set_geometry(complaints.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1))

complaints = complaints.clip(selected_civic_league.geometry)

[x1, y1, x2, y2] = complaints.total_bounds
[x3, y3, x4, y4] = mnf.total_bounds

viewstate = du.compute_view([[x1,y1], [x2,y2], [x3,y3], [x4,y4]])

complaintLayer = pdk.Layer(
    'ScatterplotLayer', 
    complaints,
    id='complaints',
    get_radius='10',
    pickable=True,
    auto_highlight=True,
    get_position=['longitude', 'latitude'],
    get_fill_color='[0, 255, 122]',
    )

deck = pdk.Deck(layers=[complaintLayer],
                tooltip={"text":"{type}/{subtype}: {status}"},
                initial_view_state=viewstate
                )

f"""
# Complaints : {len(complaints)}

"""

st.write(complaints)

st.altair_chart(
    alt.Chart(complaints).mark_tick().encode(
        alt.X('created_date:T'),
        alt.Y('type:N'),
        alt.Color('department_responsible:N')
    ).add_params(alt.selection_interval(encodings=['x'])),
    key='complaints_timeline'
    )

st.pydeck_chart(deck)