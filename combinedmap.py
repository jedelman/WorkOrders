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
    complaints = complaints.query(f"address == '{address}'")
    trees = trees.query(f"location == '{address}'")

if 'timeline_select' in st.session_state and len(st.session_state['timeline_select']) == 2:
    from datetime import datetime
    def clear_timeline():
        del st.session_state['timeline_select']

    start, end = st.session_state['timeline_select']

    datestart = datetime.fromtimestamp(start/1000)
    dateend = datetime.fromtimestamp(end/1000)

    st.button(f'selected timeline:{datestart.strftime("%D")} to {dateend.strftime("%D")}', on_click=clear_timeline)
    
    mnf = mnf[mnf['creation_date'].map(datetime.fromisoformat).between(datestart, dateend)]
    complaints = complaints[complaints['created_date'].map(datetime.fromisoformat).between(datestart, dateend)]


mnf[['longitude', 'latitude']] = mnf.get_coordinates()

import pandas as pd
coords = pd.concat([mnf[['longitude', 'latitude']], complaints[['longitude', 'latitude']], trees[['longitude', 'latitude']]])

viewstate = du.compute_view(coords)

viewstate.pitch = 50

categorycolors = du.assign_random_colors(mnf['service_request_category'])

mnf['color'] = mnf['service_request_category'].map(categorycolors)

def mnf_tooltip(row):
    return f"""
<h2>MyNorfolk Request #{row["service_request_number"]}<h2>
<p>{row['service_request_category']} : {row['service_request_type']} ({row['status']})</p>
<p>created {row["creation_date"]}</p>
<p>last modified {row["modification_date"]}</p>

    """

def complaint_tooltip(row):
    return f"""
<h2>Complaint {row["complaint_id"]}</h2>
<h3>{row["address"]}</h3>
<p>{row["type"]}, {row["subtype"]} ({row["origin"]}): {row["status"]}</p>
<p>created {row["created_date"]}</p>
<p>last modified {row["last_modified_date"]}</p>
<p>closed {row["closed_date"]}</p>

    """

def tree_tooltip(row):
    return f"""
<h2>City Tree {row["tree_id"]}:</h2>
<p>{row["common_name"]}</p>
<p>diameter: {row["trunk_diameter"]} in.</p>
    """


mnf["tooltip_text"] = mnf.apply(mnf_tooltip, axis=1)
complaints["tooltip_text"] = complaints.apply(complaint_tooltip, axis=1)
trees["tooltip_text"] = trees.apply(tree_tooltip, axis=1)

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
    get_color='color')

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
    get_radius='trunk_diameter',
    radius_scale=0.0254,
    get_elevation='trunk_diameter',
    get_position=['longitude', 'latitude'],
    get_fill_color='[0, 255, 122]')

with st.popover("Help", icon=":material/help:"):
    """# Combined Map

    This map shows trees (green), complaints (blue), and My Norfolk requests(other).

    A timeline of request types is shown below the map.

    Selecting a point will display info about the tree, or the address. 

    If an address is selected, a timeline of MyNorfolk requests associated with that address will be displayed below the map.

    """

deck = pdk.Deck(layers=[treelayer, mnflayer, complaintslayer], 
                tooltip={"html":"{tooltip_text}"},
                initial_view_state=viewstate)


def select_address():
    with st.popover("debug"):
        st.session_state
    try:
        selected_objects = st.session_state['combined_chart']['selection']['objects']
        if 'mnf' in selected_objects:
            st.session_state['selected_address'] = selected_objects['mnf'][0]['full_address']
        if 'trees' in selected_objects:
            st.session_state['selected_address'] = selected_objects['trees'][0]['location']
        if 'complaints' in selected_objects:
            st.session_state['selected_address'] = selected_objects['complaints'][0]['address']

    except:
        None

st.pydeck_chart(deck, key="combined_chart", on_select=select_address)

def select_date_interval():
    st.session_state['timeline_select'] = st.session_state['timeline_chart']['selection']['param_1']['yearmonth_creation_date']

import altair as alt

if 'selected_address' in st.session_state:
    if len(mnf) > 0:
        st.altair_chart(
            alt.Chart(mnf).mark_rule().encode(
                alt.X('creation_date:T').axis(None),
                alt.Color('service_request_category').legend(None)
            ).properties(
                height=100
            ),
            key="mnf_chart"
        )
    if len(complaints) > 0:
        st.altair_chart(
            alt.Chart(complaints).mark_rule().encode(
                alt.X('created_date:T').axis(None),
                alt.Color('type:N').legend(None)
            ).properties(
                height=100
            ),
            key="complaints_chart"
        )
else:
    param = alt.selection_interval()
    mnf_chart = alt.Chart(mnf).mark_area().encode(
            alt.X('yearmonth(creation_date):T').axis(None), 
            alt.Y('count()').axis(None),
            alt.Color('service_request_category').legend(None)
            ).properties(
                height=100
            ).add_params(
                param
            )
    complaints_chart = alt.Chart(complaints).mark_area().encode(
            alt.X('yearmonth(created_date):T').axis(None), 
            alt.Y('count()').axis(None),
            alt.Color('type').legend(None)
            ).properties(
                height=100
            ).add_params(
                param
            )
    st.altair_chart(mnf_chart,
                     key='timeline_chart', on_select=select_date_interval)
    st.altair_chart(complaints_chart,
                     key='complaints_timeline_chart')


if len(trees) > 0:
    with st.expander("trees"):
        trees

if len(mnf) > 0:
    with st.expander("MyNorfolk requests"):
        mnf

if len(complaints) > 0:
    with st.expander("Complaints"):
        complaints