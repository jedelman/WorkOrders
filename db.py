import streamlit as st
import pandas as pd
import geopandas as gpd
from sodapy import Socrata
from sqlalchemy import create_engine

class DB_NAMES:
    ADDRESSES = 'norfolk_addresses'
    MYNORFOLK = 'mynorfolk'
    COMPLAINTS = 'complaints'
    CIVIC_LEAGUES = 'civic_leagues'

class DB_QUERIES:
    def GET_MNF_BY_CIVIC_LEAGUE(league):
        return f"""
select mnf.*, na.geometry
from {DB_NAMES.CIVIC_LEAGUES} cl
join {DB_NAMES.ADDRESSES} na on cl.geometry && na.geometry
join {DB_NAMES.MYNORFOLK} mnf on mnf.full_address = na.full_address
where cl."LEAGUE" = '{league}';
    """

    def GET_COMPLAINTS_BY_CIVIC_LEAGUE(league):
        return f"""
select c.*
from {DB_NAMES.CIVIC_LEAGUES} cl
join {DB_NAMES.COMPLAINTS} c on st_contains(cl.geometry, st_point(longitude, latitude, 4326))
where cl."LEAGUE" = '{league}'
        """

# Fetch variables
USER = st.secrets["user"]
PASSWORD = st.secrets["password"]
HOST = st.secrets["host"]
PORT = st.secrets["port"]
DBNAME = st.secrets["dbname"]

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DBNAME}?sslmode=require"
engine = create_engine(DATABASE_URL)

def get_from_pg(query):
    return pd.read_sql_query(query, engine)

def get_saved_sessions_from_pg():
    return get_from_pg("SELECT * from saved_session_views")

class socrata_db_codes:
    WORK_ORDERS = "qzfe-wj25"
    COMPLAINTS = "m9m3-wk2s"
    EXPENDITURES = "mdwe-dquf"
    REVENUES = "id3i-2az4"
    MYNORFOLK = "nbyu-xjez"
    ADDRESSES = "ere7-kake"
    TREES = "cmvv-agyb"

def get_civic_leagues_from_local_file():
    return gpd.read_file('Civic_Leagues.geojson')

@st.cache_resource
def get_client():
    return Socrata("data.norfolk.gov", st.secrets["app_token"])

@st.cache_data
def get_db(db_code):
    localfile = f"data/{db_code}.csv"
    try:
        all = pd.read_csv(localfile)
    except OSError:
        all = pd.DataFrame(get_client().get_all(db_code))
        all.to_csv(localfile)
    
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
def get_complaints_from_postgis_by_cl(league):
    return pd.read_sql_query(DB_QUERIES.GET_COMPLAINTS_BY_CIVIC_LEAGUE(league), engine)

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
def get_mnf_from_socrata(query=''):
    return get_db(socrata_db_codes.MYNORFOLK)

@st.cache_data
def get_mnf(query=''):
    return gpd.read_postgis('mynorfolk', engine, geom_col="geometry")

@st.cache_data
def get_mnf_postgis_by_cl(civic_league):
    return gpd.read_postgis(DB_QUERIES.GET_MNF_BY_CIVIC_LEAGUE(civic_league), engine, geom_col='geometry')

@st.cache_data
def get_addresses():
    return gpd.read_postgis('norfolk_addresses', geom_col="geometry", con=engine)

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
def get_trees_from_local_db(query=''):

    @st.cache_data
    def get_tree_db():
        return get_db(socrata_db_codes.TREES)
    
    alldata = get_tree_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)

SEARCH_QUERY = "search_query"

def buildQuery(extras = []):
    import re

    civic_leagues = re.sub(' and |,', '/ ', st.session_state["selected_civic_league"])

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
