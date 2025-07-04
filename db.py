import streamlit as st
import pandas as pd
from sodapy import Socrata

WORK_ORDERS = "qzfe-wj25"

@st.cache_resource
def get_client():
    return Socrata("data.norfolk.gov", st.secrets["app_token"])

@st.cache_data
def get_work_order_db():
    return pd.DataFrame(get_client().get_all(WORK_ORDERS))

@st.cache_data
def get_work_orders_from_local_db(query):
    alldata = get_work_order_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)
