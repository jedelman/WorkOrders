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

mnf = db.get_mnf_postgis_by_cl(st.session_state["selected_civic_league"])

mnf[['longitude', 'latitude']] = mnf.get_coordinates()

viewstate = du.compute_view(mnf['geometry'].get_coordinates())

viewstate.pitch = 50

categorycolors = du.assign_random_colors(mnf['service_request_category'])

mnf['color'] = mnf.apply(lambda row: categorycolors[row['service_request_category']],axis=1)

mnflayer = pdk.Layer(
    'GridLayer',
    mnf,
    id='mnf',
    pickable=True,
    auto_highlight=True,
    extruded=True,
    cell_size=4,
    get_position=['longitude', 'latitude'],
    radius=2,
    get_fill_color='color')

deck = pdk.Deck(layers=[mnflayer], 
                tooltip={"text":"{elevationValue}"},
                initial_view_state=viewstate)

selection = st.pydeck_chart(deck, key="mnf_chart", on_select="rerun")

import altair as alt
timeline = st.altair_chart(
    alt.Chart(mnf).mark_area().encode(
        alt.X('yearmonth(creation_date):T').axis(None), 
        alt.Y('count()').axis(None),
        alt.Color('service_request_category').legend(None)
        ).properties(
            height=100
        ))

st.write(st.session_state['mnf_chart'])

st.write(mnf)