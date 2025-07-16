import streamlit as st
import pandas as pd
from sodapy import Socrata

WORK_ORDERS = "qzfe-wj25"
COMPLAINTS = "m9m3-wk2s"
EXPENDITURES = "mdwe-dquf"
REVENUES = "id3i-2az4"
MYNORFOLK = "nbyu-xjez"

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
def get_work_order_db():
    return get_db(WORK_ORDERS)
    
@st.cache_data
def get_complaint_db():
    return get_db(COMPLAINTS)

@st.cache_data
def get_expenditure_db():
    return get_db(EXPENDITURES)

@st.cache_data
def get_work_orders_from_local_db(query=''):
    alldata = get_work_order_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)

@st.cache_data
def get_complaints_from_local_db(query=''):
    alldata = get_complaint_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)

@st.cache_data
def get_expenditures_from_local_db(query=''):
    alldata = get_expenditure_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)

@st.cache_data
def get_mnf_from_local_db(query=''):
    
    @st.cache_data
    def get_mnf_db():
        return get_db(MYNORFOLK)
    
    alldata = get_mnf_db()
    if(query == ''):
        return alldata
    
    return alldata.query(query)