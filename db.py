import streamlit as st
import pandas as pd
from sodapy import Socrata

@st.cache_resource
def get_client():
    return Socrata("data.norfolk.gov", st.secrets["app_token"])

@st.cache_data
def get_work_orders(_client, query):
    work_orders = "qzfe-wj25"
    return pd.DataFrame(_client.get(work_orders, where=' and '.join(query)))
