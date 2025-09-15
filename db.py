import streamlit as st
import pandas as pd
import geopandas as gpd
from sodapy import Socrata

class socrata_db_codes:
    WORK_ORDERS = "qzfe-wj25"
    COMPLAINTS = "m9m3-wk2s"
    EXPENDITURES = "mdwe-dquf"
    REVENUES = "id3i-2az4"
    MYNORFOLK = "nbyu-xjez"
    ADDRESSES = "ere7-kake"
    TREES = "cmvv-agyb"

@st.cache_resource
def get_client():
    return Socrata("data.norfolk.gov", st.secrets["app_token"])

@st.cache_data
def get_db(db_code, query=''):
    if query == '':
        all = pd.DataFrame(get_client().get_all(db_code))
    else:
        all = pd.DataFrame(get_client().get(db_code, where=query))
    return all

@st.cache_data
def work_orders_fulltext_search(query, filter=''):
    all = pd.DataFrame(get_client().get(socrata_db_codes.WORK_ORDERS, q=query))
    if not filter == '':
        all = all.query(filter)
    return all

@st.cache_data
def get_work_orders_from_local_db(query=''):
    @st.cache_data
    def get_work_order_db():
        return get_db(socrata_db_codes.WORK_ORDERS)


    alldata = get_work_order_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)

@st.cache_data
def get_complaints_from_local_db(query=''):
    @st.cache_data
    def get_complaint_db():
        return get_db(socrata_db_codes.COMPLAINTS)


    alldata = get_complaint_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)

@st.cache_data
def get_expenditures_from_local_db(query=''):

    @st.cache_data
    def get_expenditure_db():
        return get_db(socrata_db_codes.EXPENDITURES)

    alldata = get_expenditure_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)

@st.cache_data
def get_mnf(query=''):
    return get_db(socrata_db_codes.MYNORFOLK)

@st.cache_data
def get_addresses_from_local_db(query=''):
    @st.cache_data
    def get_addr_db():
        return get_db(socrata_db_codes.ADDRESSES)


    import geopandas as gpd
    import shapely
    import json
    import re

    quotefix = re.compile("'")

    addrs = gpd.GeoDataFrame(get_addr_db())
    addrs = addrs.dropna(subset=['geocoded_column'])

    def convertgeo(item):
        try:
            return shapely.geometry.shape(
                json.loads(
                    quotefix.sub('"', item)))
        except Exception as x:
            print({"ERROR":"ERROR", "item":item, "x":x})

    addrs['geometry'] = addrs['geocoded_column'].apply(convertgeo)
    
    if(query == ''):
        return addrs
    
    return addrs.query(query)

@st.cache_data
def get_trees_from_local_db(query='', filter=''):

    @st.cache_data
    def get_tree_db():
        return get_db(socrata_db_codes.TREES)
    
    if(query == ''):
        alldata = get_tree_db()
    else:
        alldata = get_client().get(socrata_db_codes.TREES, q=query)

    if(filter == ''):
        return alldata
    else:
        return alldata.query(filter)

SEARCH_QUERY = "search_query"

def buildQuery(extras = []):
    import re

    civic_leagues = re.sub(' and |,', '/ ', st.session_state.get("selected_civic_league", "Ghent Neighborhood League"))

    q = [
        f"{key} in ({value})"
        for key, value in 
        st.session_state[SEARCH_QUERY].items()]

    if 'dates' in st.session_state:
        start, end = st.session_state.dates
        q.append(f"start_date >= '{(start)}' and start_date <= '{(end)}'")

    q.append(f"civic_league in ['{civic_leagues}']")
    
    for x in extras:
        q.append(x)

    query = ' and '.join(q)
    return query
