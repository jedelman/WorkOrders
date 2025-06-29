# python3 -m streamlit run sandbox-streamlit.py
import streamlit as st
from sodapy import Socrata
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

app_token =  "6Te8cUPiKLtDiuU9kxxMaTV5y"
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

area = st.sidebar.multiselect("Area", options=['Forestry', 'Landscape', 'Traffic', 'Streets', 'Stormwater',
       'Street Sweeping', 'Bridges', 'Environmental', 'Streets_Bridges',
       'Wastewater', 'Miscellaneous', 'Water Distribution',
       'Special Events'])

cats = st.sidebar.multiselect("Category", options=get_categories())
status_codes = st.sidebar.multiselect("Status Codes", options=get_status_codes())
startdate, enddate = st.sidebar.date_input("Date", value=(datetime.today(), datetime.today() + timedelta(days=7)))
civicleagues = st.sidebar.multiselect("Civic League", options = get_civic_leagues())

work_orders = "qzfe-wj25"

query = f"start_date between '{startdate.isoformat()}' and '{enddate.isoformat()}'"

if len(civicleagues) > 0:
    cl = ', '.join([f"'{x}'" for x in civicleagues])
    query += f" and civic_league in ({cl})"

if len(area) > 0:
    areas = ', '.join([f"'{x}'" for x in area])
    query +=  f" and area in({areas})"

if len(status_codes) > 0:
    status_codes = ', '.join([f"'{x}'" for x in status_codes])
    query += f" and status_description in ({status_codes})"


with st.sidebar.popover("", icon=":material/help:"):
    query

client = get_client()

try:        
    items = pd.DataFrame(client.get(work_orders, where=query))

    f"got {items.index.size} work orders"

    if(items.index.size > 0):
        f"total cost: {items['total_cost'].astype(np.float64).sum()}"
    
    items
except Exception as ex:
    ex
