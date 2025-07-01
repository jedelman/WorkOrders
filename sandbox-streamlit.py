import streamlit as st
from sodapy import Socrata
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from string import Template

app_token =  st.secrets["app_token"]

header = st.container()

itemcnt, debugcnt = st.tabs(["items", "debug"])

with debugcnt:
    debugcnt.title("session state")
    debugcnt.write(st.session_state)

@st.cache_resource
def get_client():
    return Socrata("data.norfolk.gov", app_token)

@st.cache_data
def get_categories():
    return pd.read_csv("categories.csv")["Category Description"]

@st.cache_data
def get_civic_leagues():
    return pd.read_csv("civic_leagues.csv")['0']

@st.cache_data
def get_status_codes():
    return np.load("status_descriptions.npy", allow_pickle=True)

def qp_init(key):
    if key not in st.session_state and key in st.query_params:
        st.session_state[key] = st.query_params.get_all(key)

def qp_set_on_search(key):
    if key in st.session_state:
        st.query_params[key] = st.session_state[key]
    return st.query_params.get_all(key)

query = ""

param_index = [
    'area', 
    'cats',  
    'status_codes', 
    'civic_league', 
    'dates' ]

debugcnt.title("qp init")
debugcnt.write([qp_init(key) for key in param_index])
debugcnt.write([st.session_state[key] for key in param_index if key in st.session_state])

st.sidebar.multiselect("Area", key="area", options=['', 'Forestry', 'Landscape', 'Traffic', 'Streets', 'Stormwater',
       'Street Sweeping', 'Bridges', 'Environmental', 'Streets_Bridges',
       'Wastewater', 'Miscellaneous', 'Water Distribution',
       'Special Events'])
st.sidebar.multiselect("Category", key="category_description", options=get_categories())
st.sidebar.multiselect("Status Codes", key="status_code", options=get_status_codes())

if("dates" in st.session_state):
    if(type(st.session_state.dates) is str):
        st.session_state.dates = datetime(st.session_state.dates)
            

st.sidebar.date_input("Date", key="dates")

def YTD_click():
    st.session_state["dates"] = [datetime(year = datetime.now().year, month=1, day=1) ,datetime.today()]

st.sidebar.button("YTD", on_click=YTD_click)

if "dates" in st.session_state:
    match st.session_state["dates"]:
        case startdate, enddate:
            query += f"start_date between '{startdate.isoformat()}' and '{enddate.isoformat()}'"
        case datetime():
            date = st.session_state["dates"]
            query += f"start_date = '{date.isoformat()}'"

st.sidebar.multiselect("Civic League", key="civic_league", options = get_civic_leagues())

for column in [
    "civic_league",
    "area",
    "status_description", 
    "category_description",]:
    if column in st.session_state and len(st.session_state[column]) > 0:
        optstr = ', '.join([f"'{x}'" for x in st.session_state[column]])
        query += f" and {column} in ({optstr})"

debugcnt.write(query)

client = get_client()

md_template = Template(open("row_template.md").read())

def timefmt(str):
    return datetime.fromisoformat(str).strftime("%m/%d/%Y") if type(str) is str else None

def display_items(items):
    if items is None or len(items) == 0:
        return "nothing to show"

    for row in items.to_dict('records'):
        row["start_date_fmt"] = timefmt(row["start_date"])
        row["status_datetime_fmt"] = timefmt(row["status_datetime"])
        row["created_datetime_fmt"] = timefmt(row["created_datetime"])
        try:
            itemcnt.markdown(md_template.safe_substitute(row))
        except Exception as Ex:
            itemcnt.write(Ex)
        with itemcnt.expander("raw data"):
            row



@st.cache_data
def get_items(query):
    work_orders = "qzfe-wj25"        
    return client.get(work_orders, where=query)

try:
    items = None
    debugcnt.title("query info")
    debugcnt.write([qp_set_on_search(key) for key in param_index])


    items = pd.DataFrame(get_items(query))
    itemindex = itemcnt.slider("browse items", key="itemindex", max_value=items.index.size)
    wocnt, cost = header.columns(2)
    wocnt.metric("Work orders", value=items.index.size)
    
    if(items.index.size > 0):
        cost.metric("Total Cost", value=items['total_cost'].astype(np.float64).sum())
    selected = items.loc[[itemindex]]
    debugcnt.write(items)
    debugcnt.write(f"item index: {itemindex}")
    debugcnt.write("selected items")
    debugcnt.write(selected)

    display_items(selected)

except Exception as ex:
    itemcnt.error("Error encountered!")
    debugcnt.write(ex)
