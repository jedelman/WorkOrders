import streamlit as st
import pydeck as pdk
import pydeck.data_utils as du
import db
import re

st.set_page_config(layout='wide')

civic_leagues = re.sub(' and |,', '/ ', st.session_state["selected_civic_league"])

civic_leagues = f'civic_league in ["{civic_leagues}"]'

trees = db.get_trees_from_local_db(civic_leagues)

viewstate = du.compute_view(trees[["longitude", "latitude"]])

treelayer = pdk.Layer(
    'ScatterplotLayer',
    trees,
    id='trees',
    get_radius='trunk_diameter',
    radius_scale=0.25,
    pickable=True,
    auto_highlight=True,
    get_position=['longitude', 'latitude'],
    get_fill_color='[0, 255, 122]')

treedensitylayer = pdk.Layer(
    'HeatmapLayer',
    trees, 
    opacity=0.75,
    id='treedensity',
    get_position=['longitude', 'latitude']
)

deck = pdk.Deck(layers=[treedensitylayer, treelayer], 
                tooltip={"text":"{common_name}: {trunk_diameter} in"},
                initial_view_state=viewstate)

cols = st.columns(2)

def select_tree():
    if 'trees' in st.session_state:
        selected_trees = st.session_state['trees']['selection']['objects']
        if 'trees' in selected_trees:
            st.session_state['selected_trees'] = selected_trees['trees']

selection = cols[0].pydeck_chart(deck,   
                                 key='trees', on_select=select_tree)

with cols[1]:
    """
    # Tree inspector

    pan and zoom the map to examine current city tree inventory.

    click on a tree to view its inventory code and additional stats about it.

    """

    if 'selected_trees' in st.session_state:
        for tree in st.session_state['selected_trees']:
            st.header(tree['tree_id'])
            st.write(tree['common_name'])
            st.caption(f"{tree['genus']} {tree['species']}")
            st.metric(label='trunk diameter', value=tree['trunk_diameter'])