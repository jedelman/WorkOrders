import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pydeck.data_utils as du
import db
import shapely
import json
import re

quotefix = re.compile("'")

def convertgeo(item):
    try:
        return shapely.geometry.shape(
            json.loads(
                quotefix.sub('"', item)))
    except Exception as x:
        print({"ERROR":"ERROR", "item":item, "x":x})

st.set_page_config(layout='wide')

league = st.session_state["selected_civic_league"]

mnf = db.get_mnf_postgis_by_cl(league)

complaints = db.get_complaints_from_postgis_by_cl(league)

civic_leagues = re.sub(' and |,', '/ ', st.session_state["selected_civic_league"])

civic_leagues = f'civic_league in ["{civic_leagues}"]'

trees = db.get_trees_from_local_db(civic_leagues)

if 'selected_address' in st.session_state:
    address = st.session_state['selected_address'] 
    def clear_address():
        del st.session_state['selected_address']

    st.button(f"selected address: {address}", on_click=clear_address)

    mnf = mnf.query(f"full_address == '{address}'")

if 'timeline_select' in st.session_state and len(st.session_state['timeline_select']) == 2:
    from datetime import datetime
    def clear_timeline():
        del st.session_state['timeline_select']

    start, end = st.session_state['timeline_select']

    datestart = datetime.fromtimestamp(start/1000)
    dateend = datetime.fromtimestamp(end/1000)

    st.button(f'selected timeline:{datestart.strftime("%D")} to {dateend.strftime("%D")}', on_click=clear_timeline)
    
    mnf = mnf[mnf['creation_date'].map(datetime.fromisoformat).between(datestart, dateend)]


mnf[['longitude', 'latitude']] = mnf.get_coordinates()

viewstate = du.compute_view(mnf['geometry'].get_coordinates())

viewstate.pitch = 50

categorycolors = du.assign_random_colors(mnf['service_request_category'])

mnf['color'] = mnf.apply(lambda row: categorycolors[row['service_request_category']],axis=1)


mnflayer = pdk.Layer(
    'ScatterplotLayer',
    mnf,
    id='mnf',
    gpu_aggregation=True,
    pickable=True,
    auto_highlight=True,
    extruded=True,
    cell_size=4,
    get_position=['longitude', 'latitude'],
    radius=2,
    get_fill_color='color')

complaintslayer = pdk.Layer(
    'ScatterplotLayer',
    complaints,
    id='complaints',
    gpu_aggregation=True,
    pickable=True,
    auto_highlight=True,
    get_position=['longitude', 'latitude'],
    radius=2,
    get_fill_color='[0, 122, 255]'
)

treelayer = pdk.Layer(
    'ScatterplotLayer',
    trees,
    id='trees',
    pickable=True,
    auto_highlight=True,
    extruded=True,
    get_elevation='trunk_diameter',
    get_position=['longitude', 'latitude'],
    get_fill_color='[0, 255, 122]')

deck = pdk.Deck(layers=[mnflayer, complaintslayer, treelayer], 
                tooltip=True,
                initial_view_state=viewstate)

def select_address():
    st.session_state
    try:
        st.session_state['selected_address'] = st.session_state['mnf_chart']['selection']['objects']['mnf'][0]['full_address']
    except:
        None

st.pydeck_chart(deck, key="mnf_chart", on_select=select_address)

def select_date_interval():
    st.session_state['timeline_select'] = st.session_state['timeline_chart']['selection']['param_1']['yearmonth_creation_date']

import altair as alt

if 'selected_address' in st.session_state:
    st.altair_chart(
        alt.Chart(mnf).mark_circle().encode(
            alt.X('creation_date:T').axis(None),
            alt.Color('service_request_category').legend(None)
        ).properties(
            height=100
        )
    )
else:
    st.altair_chart(
        alt.Chart(mnf).mark_area().encode(
            alt.X('yearmonth(creation_date):T').axis(None), 
            alt.Y('count()').axis(None),
            alt.Color('service_request_category').legend(None)
            ).properties(
                height=100
            ).add_params(
                alt.selection_interval()
            ), key='timeline_chart', on_select=select_date_interval)


