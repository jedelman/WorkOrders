import streamlit as st
from sodapy import Socrata
from db import get_client, get_work_orders
from render_work_order import render_work_order

st.set_page_config(page_title="Norfolk Work Orders Detail", page_icon=":city_sunrise:", layout="wide")

WORK_ORDER_ID = "work_order_number"

if(WORK_ORDER_ID in st.query_params):
    st.session_state[WORK_ORDER_ID] = st.query_params[WORK_ORDER_ID]

st.page_link("orders-search.py", label="<<< Back to Search")

wo_id = st.text_input("Enter a Work Order ID", key=WORK_ORDER_ID)

if wo_id == '' or wo_id is None:
    None
else:
    items = get_work_orders(get_client(), [f"{WORK_ORDER_ID} = '{wo_id}'"])
    render_work_order(st.container(), items.to_dict("records")[0])
