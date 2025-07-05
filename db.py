import streamlit as st
import pandas as pd
from sodapy import Socrata

WORK_ORDERS = "qzfe-wj25"

@st.cache_resource
def get_client():
    return Socrata("data.norfolk.gov", st.secrets["app_token"])

LOCAL_WORK_ORDER_FILE = "workorders-df.pydata"

@st.cache_data
def get_work_order_db():
    try:
        allorders = pd.read_csv(LOCAL_WORK_ORDER_FILE)
    except OSError:
        allorders = pd.DataFrame(get_client().get_all(WORK_ORDERS))
        allorders.to_csv(LOCAL_WORK_ORDER_FILE)
    
    return allorders

@st.cache_data
def get_work_orders_from_local_db(query):
    alldata = get_work_order_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)
