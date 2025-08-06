import streamlit as st
import pydeck as pdk
import pydeck.data_utils as du
import geopandas as gpd

st.set_page_config(page_title="Civic League selection", layout="wide")

if not 'selected_civic_league' in st.session_state:
    """
    # Welcome!
    Please select your civic league.

    There is TOO MUCH DATA to look at the whole city at once. Good job, Norfolk Open Data Team!
    """
else:
    f"""
    Selected Civic League : 
    # {st.session_state['selected_civic_league']}

    
    """

civicleagues = gpd.read_file('Civic_Leagues.geojson')

color_dict = du.assign_random_colors(civicleagues['LEAGUE'])

#viewstate = pdk.ViewState(latitude=36.8508, longitude=-76.2859, zoom=11, pitch=0)

[x1,y1,x2,y2] = civicleagues.total_bounds

viewstate = du.compute_view([[x1,y1],[x2,y2]])

# Define a layer to display on a map
layer = pdk.Layer(
    'GeoJsonLayer',
    civicleagues,
    id="civic_leagues",
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

deck = pdk.Deck(layer, 
                tooltip={"text":"{LEAGUE}"},
                initial_view_state=viewstate)


def select_cl():
    map_objs = st.session_state['cl_map']['selection']['objects']
    if 'civic_leagues' in map_objs:
        cl = map_objs['civic_leagues'][0]['LEAGUE']
        if 'selected_civic_league' not in st.session_state or cl != st.session_state['selected_civic_league']:
            st.session_state['selected_civic_league'] = cl
    else:
        del st.session_state['selected_civic_league']
    

st.pydeck_chart(deck, key="cl_map", on_select=select_cl)