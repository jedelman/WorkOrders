import streamlit as st
import pydeck as pdk
import pydeck.data_utils as du
import db

st.set_page_config(layout='wide')

trees = db.get_trees_from_local_db('civic_league == "Ghent Neighborhood League"')

viewstate = pdk.ViewState(latitude=36.8508, longitude=-76.2859, zoom=13, pitch=45, bearing=10)

# Define a layer to display on a map
treelayer = pdk.Layer(
    'ScatterplotLayer',
    trees,
    id='trees',
    get_position=['longitude', 'latitude'],
    get_fill_color='[0, 255, 122]')

treedensitylayer = pdk.Layer(
    'HeatmapLayer',
    trees, 
    opacity=0.75,
    id='treedensity',
    get_position=['longitude', 'latitude'],
)

treenamelayer = pdk.Layer(
    'TextLayer',
    trees,
    id='treenames',
    get_position=['longitude', 'latitude'],
    get_text='common_name',
    get_size='trunk_diameter',
    pickable=True,
    auto_highlight=True,
    size_scale=0.5,
    size_units='meters',
    get_color='[0,230,186]'
)

deck = pdk.Deck(layers=[treenamelayer, treelayer, treedensitylayer], initial_view_state=viewstate)

cols = st.columns(2)

selection = cols[0].pydeck_chart(deck, key='trees', on_select="rerun")

with cols[1]:
    try:
        tree = selection.selection['objects']['treenames'][0]
        st.header(tree['tree_id'])
        st.write(tree['common_name'])
        st.caption(f"{tree['genus']} {tree['species']}")
        st.metric(label='trunk diameter', value=tree['trunk_diameter'])
        st.write(selection)
    except Exception as x:
        st.write()