import streamlit as st
from sodapy import Socrata
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

app_token =  st.secrets["app_token"]

header = st.container()

itemcnt, debugcnt = st.tabs(["items", "debug"])

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

query = []

param_index = [
    'area', 
    'category_description',  
    'status_codes', 
    'civic_league', 
    'dates' ]

debugcnt.title("qp init")
debugcnt.write([qp_init(key) for key in param_index])
if("dates" in st.session_state):
    if(type(st.session_state.dates) is str):
        st.session_state.dates = datetime(st.session_state.dates)
    if(type(st.session_state.dates) is list):
        if(type(st.session_state.dates[0]) is str):
            st.session_state.dates = [datetime.strptime(date, "%Y-%m-%d") for date in list(st.session_state.dates)]

debugcnt.write([st.session_state[key] for key in param_index if key in st.session_state])

st.sidebar.multiselect("Area", key="area", options=['', 'Forestry', 'Landscape', 'Traffic', 'Streets', 'Stormwater',
       'Street Sweeping', 'Bridges', 'Environmental', 'Streets_Bridges',
       'Wastewater', 'Miscellaneous', 'Water Distribution',
       'Special Events'])
st.sidebar.multiselect("Category", key="category_description", options=get_categories())
st.sidebar.multiselect("Status Codes", key="status_code", options=get_status_codes())

            

st.sidebar.date_input("Date", key="dates")

def YTD_click():
    st.session_state["dates"] = [datetime(year = datetime.now().year, month=1, day=1) ,datetime.today()]

st.sidebar.button("YTD", on_click=YTD_click)

if "dates" in st.session_state:
    match st.session_state["dates"]:
        case startdate, enddate:
            query.append(f"start_date between '{startdate.isoformat()}' and '{enddate.isoformat()}'")
        case datetime():
            date = st.session_state["dates"]
            query.append(f"start_date = '{date.isoformat()}'")

st.sidebar.multiselect("Civic League", key="civic_league", options = get_civic_leagues())

for column in [
    "civic_league",
    "area",
    "status_description", 
    "category_description",]:
    if column in st.session_state and len(st.session_state[column]) > 0:
        optstr = ', '.join([f"'{x}'" for x in st.session_state[column]])
        query.append(f" and {column} in ({optstr})")

debugcnt.write(query)

client = get_client()

def datefmt(datestr):
    return datetime.fromisoformat(datestr).strftime("%m/%d/%Y") if type(datestr) is str else None

def display_items(items):
    if items is None or len(items) == 0:
        return "nothing to show"

    for row in items.to_dict('records'):
        row["start_date_fmt"] = datefmt(row["start_date"])
        row["status_datetime_fmt"] = datefmt(row["status_datetime"])
        row["created_datetime_fmt"] = datefmt(row["created_datetime"])
        try:
            renderitem(row)
        except Exception as Ex:
            itemcnt.write(Ex)
        

def renderitem(row):
    rowcnt, debugrowcnt = itemcnt.tabs(["work order", "raw data"])
    debugrowcnt.write(row)
    rowcnt.title(row.get("work_order_number"))
    rowcnt.caption("work order number")
    cols = rowcnt.columns(3)
    def setstate(key, newstate):
        st.session_state[key] = newstate
    

    cat = row.get("category_description")
    cols[0].button(cat, on_click=setstate, args=["category_description", [cat]])
    cols[0].caption("Category")
    cols[1].write(row.get("primary_task_description"))
    cols[1].caption("Action")
    cols[2].write(row.get("total_cost"))
    cols[2].caption("Total Cost")

    cols = rowcnt.columns(3)
    cols[0].write(row.get("created_datetime_fmt"))
    cols[0].caption("Created")
    cols[1].write(row.get("start_date_fmt"))
    cols[1].caption("Started")
    cols[2].write(row.get("status_description"))
    cols[2].write(row.get("status_datetime_fmt"))
    cols[2].caption("Updated")
    

    cols = rowcnt.columns(3)
    cols[0].write(row.get('problem_description'))
    cols[0].caption("Problem")
    cols[1].write(row.get("priority"))
    cols[1].caption("Priority")
    
    cols = rowcnt.columns(3)
    cl = row.get("civic_league")
    if type(cl) is str:
        cols[0].button(cl, on_click=setstate, args=["civic_league", [cl]])
    else:
        cols[0].write(cl)
    cols[0].caption("Civic League")
    cols[1].write(row.get("street"))
    cols[1].caption("Street")
        

@st.cache_data
def get_items(query):
    work_orders = "qzfe-wj25"        
    return client.get(work_orders, where=' and '.join(query))

try:
    items = None
    debugcnt.title("query info")
    debugcnt.write([qp_set_on_search(key) for key in param_index])


    items = pd.DataFrame(get_items(query))
    wocnt, cost = header.columns(2)
    wocnt.metric("Work orders", value=items.index.size)
    
    if(items.index.size > 0):
        itemindex = itemcnt.number_input("browse items", key="itemindex", min_value=0, max_value=items.index.size)
        selected = items.loc[[itemindex]]
        debugcnt.write(items)
        debugcnt.write(f"item index: {itemindex}")
        debugcnt.write("selected items")
        debugcnt.write(selected)

        display_items(selected)

except Exception as ex:
    itemcnt.error("Error encountered!")
    debugcnt.write(ex)
