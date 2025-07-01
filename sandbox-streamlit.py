import streamlit as st
from sodapy import Socrata
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from string import Template

app_token =  st.secrets["app_token"]

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

def qp_init(key, default):
    if key not in st.session_state and key in st.query_params:
        st.session_state[key] = st.query_params.get_all(key)
    else:
        st.session_state[key] = default
    return st.session_state[key]

def qp_set_on_search(key):
    if key in st.session_state:
        st.query_params[key] = st.session_state[key]
        return st.query_params[key]

query = ""

param_index = [
    ('area', []), 
    ('cats', []), 
    ('status_codes', []), 
    ('dates', [datetime.today(), datetime.today() + timedelta(days=7)])]

debugcnt.title("qp init")
debugcnt.write([qp_init(key, default) for (key, default) in param_index])
    
st.session_state["area"] = area = st.sidebar.multiselect("Area", options=['', 'Forestry', 'Landscape', 'Traffic', 'Streets', 'Stormwater',
       'Street Sweeping', 'Bridges', 'Environmental', 'Streets_Bridges',
       'Wastewater', 'Miscellaneous', 'Water Distribution',
       'Special Events'], default=st.session_state.get("area"))

st.session_state["cats"] = cats = st.sidebar.multiselect("Category", options=get_categories(), default=st.session_state['cats'])

st.session_state["status_codes"] = status_codes = st.sidebar.multiselect("Status Codes", options=get_status_codes(), default=st.session_state['status_codes'])

st.session_state["dates"] = dates = st.sidebar.date_input("Date", value=st.session_state["dates"])

match len(dates):
    case 2:
        startdate, enddate = dates
        query += f"start_date between '{startdate.isoformat()}' and '{enddate.isoformat()}'"
    case 1:
        date = dates[0]
        query += f"start_date = '{date.isoformat()}'"
    case 0:
        query += ""

civicleagues = st.sidebar.multiselect("Civic League", options = get_civic_leagues())

for (column, opts) in [
    ("civic_league", civicleagues),
    ("area", area),
    ("status_description", status_codes),
    ("category_description", cats)]:
    if len(opts) > 0:
        optstr = ', '.join([f"'{x}'" for x in opts])
        query += f" and {column} in ({optstr})"

debugcnt.write(query)

client = get_client()

md_template = Template(open("row_template.md").read())

def timefmt(str):
    return datetime.fromisoformat(str).strftime("%m/%d/%Y")

def display_items(items):
    if len(items) == 0:
        return "nothing to show"
    
    for row in items.to_dict('records'):
        row["start_date_fmt"] = timefmt(row["start_date"])
        row["status_datetime_fmt"] = timefmt(row["status_datetime"])
        row["created_datetime_fmt"] = timefmt(row["created_datetime"])
        itemcnt.markdown(md_template.substitute(row))
        with itemcnt.expander("raw data"):
            row
        

try:
    work_orders = "qzfe-wj25"
    items = None
    debugcnt.title("query info")
    debugcnt.write([qp_set_on_search(key) for key in param_index])

    items = pd.DataFrame(client.get(work_orders, where=query))

    f"got {items.index.size} work orders"

    if(items.index.size > 0):
        f"total cost: {items['total_cost'].astype(np.float64).sum()}"
    
    display_items(items)
except Exception as ex:
    itemcnt.error("Error encountered!")
    debugcnt.write(ex)
