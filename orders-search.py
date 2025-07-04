import streamlit as st
import pandas as pd
import numpy as np
from db import get_client, get_work_orders_from_local_db
from datetime import datetime, timedelta
from render_work_order import render_work_order

st.set_page_config(page_title="Norfolk Work Orders Search", page_icon=":city_sunrise:", layout="wide", initial_sidebar_state="collapsed")

header = st.container()

itemcnt, statscnt, debugcnt = st.tabs(["items", "stats", "debug"])

debugcnt.title("session state")
debugcnt.write(st.session_state)

@st.cache_data
def get_categories():
    return pd.read_csv("categories.csv")["Category Description"]

@st.cache_data
def get_civic_leagues():
    return pd.read_csv("civic_leagues.csv")['0']

@st.cache_data
def get_status_codes():
    return np.load("status_descriptions.npy", allow_pickle=True)

def qp_set_on_search(key):
    if key in st.session_state:
        st.query_params[key] = st.session_state[key]
    return st.query_params.get_all(key)

searchform = st.sidebar.form("search")

def multiselect_qp_init(param):
    key = param.name
    if key not in st.session_state and key in st.query_params:
        st.session_state[key] = st.query_params.get_all(key)

def text_qp_init(param):
    key = param.name
    if key not in st.session_state and key in st.query_params:
        st.session_state[key] = ''.join(st.query_params[key])

class SearchParam:
    def __init__(self, name, widgetcb, querycb, qpinitcb = multiselect_qp_init):
        self.name = name
        self.widgetcb = widgetcb
        self.querycb = querycb
        self.qpinitcb = qpinitcb

    def widget(self):
        return self.widgetcb(self)
    
    def query(self):
        return self.querycb(self)
    
    def qpinit(self):
        return self.qpinitcb(self)


areas = ['', 'Forestry', 'Landscape', 'Traffic', 'Streets', 'Stormwater',
       'Street Sweeping', 'Bridges', 'Environmental', 'Streets_Bridges',
       'Wastewater', 'Miscellaneous', 'Water Distribution',
       'Special Events']

def multiselect_query(param):
    selections = st.session_state[param.name];
    if len(selections) == 0:
        return ''
    
    optstr = ', '.join([f"'{x}'" for x in selections])
    return f"{param.name} in ({optstr})"

def text_query(param):
    val = st.session_state[param.name]
    if(val == '' or val is None):
        return ''
    
    return f"{param.name} like upper('{val}')"

area = SearchParam('area', lambda _: searchform.multiselect("Area", key=_.name, options=areas), multiselect_query)
categories = SearchParam('category_description', 
                         lambda _: searchform.multiselect("Category", key=_.name, options=get_categories()),
                         multiselect_query)
status_codes = SearchParam('status_code', 
                           lambda _: searchform.multiselect("Status Codes", key=_.name, options=get_status_codes()),
                           multiselect_query)
civic_league = SearchParam('civic_league', 
                           lambda _: searchform.multiselect("Civic League", key=_.name, options = get_civic_leagues()),
                           multiselect_query)
street = SearchParam('street', 
                     lambda _: searchform.text_input("Street", key=_.name),
                     text_query,
                     text_qp_init)

def date_query(self):
    if self.name in st.session_state:
        match st.session_state[self.name]:
            case startdate, enddate:
                return f"start_date >= '{startdate.isoformat()}' and start_date <= '{enddate.isoformat()}'"
            case datetime():
                date = st.session_state[self.name]
                return f"start_date = '{date.isoformat()}'"
def YTD_click():
        st.session_state["dates"] = [datetime(year = datetime.now().year, month=1, day=1) ,datetime.today()]

def date_widgets(self):
    searchform.date_input("Date", key=self.name)
    header.button("YTD", on_click=YTD_click)

dates = SearchParam('dates', date_widgets, date_query)

param_index = [
    area,
    categories,
    status_codes, 
    civic_league, 
    street,
    dates
    ]


debugcnt.title("qp init")
debugcnt.write([param.qpinit() for param in param_index])

if("dates" in st.session_state):
    if(type(st.session_state.dates) is str):
        st.session_state.dates = datetime(st.session_state.dates)
    if(type(st.session_state.dates) is list):
        if(type(st.session_state.dates[0]) is str):
            st.session_state.dates = [datetime.strptime(date, "%Y-%m-%d") for date in list(st.session_state.dates)]

for param in param_index:
    param.widget()

searchform.form_submit_button("Search")

debugcnt.write([st.session_state[param.name] for param in param_index if param.name in st.session_state])

query = [q for q in [param.query() for param in param_index] if not q is '' and not q is None]

debugcnt.title("query info")
debugcnt.write([qp_set_on_search(param.name) for param in param_index])
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
            render_work_order(itemcnt, row)
        except Exception as Ex:
            itemcnt.write(Ex)
        
def display_stats(items):
    if items is None or len(items) == 0:
        return "nothing to show"

    with statscnt:

        statscnt.title("Stats")

        st.write(items)

        groupby = st.selectbox("group by", ["area", "civic_league", "problem_description", "category_description"])

        #breakdown by area
        items["total_cost"] = pd.to_numeric(items["total_cost"])

        st.bar_chart(items.groupby(groupby).sum()["total_cost"])


def nextpage():
    if("page" in st.session_state):
        st.session_state.page+=1
    else:
        st.session_state.page = 0

def prevpage():
    if("page" in st.session_state):
        st.session_state.page-=1
    else:
        st.session_state.page = 0

try:
    debugcnt.write("query=")
    debugcnt.write(' and '.join(query))
    items = get_work_orders_from_local_db(' and '.join(query))
    debugcnt.write(items)
    wocnt, cost = header.columns(2)
    wocnt.metric("Work orders", value=items.index.size)
    
    if(items.index.size > 0):
        if("page" not in st.session_state):
            st.session_state.page = 0

        prev, perpage, next = itemcnt.columns(3)
        ipp = perpage.selectbox("Items per page", [10,25,50], label_visibility="collapsed")
        startidx, endidx = st.session_state.page*ipp, min((st.session_state.page+1)*ipp, items.index.size)
        prev.button("< Prev", on_click=prevpage, disabled=st.session_state.page==0)
        next.button("Next >", on_click=nextpage, disabled=endidx>=items.index.size-1)
       
        debugcnt.write([startidx, ipp, endidx])

        selected = items.iloc[range(startidx, endidx)]

        debugcnt.write(items)
        debugcnt.write(f"page: {st.session_state.page} startidx:{startidx} endidx{endidx}")
        debugcnt.write("selected items")
        debugcnt.write(selected)

        display_items(selected)
        display_stats(items)

except Exception as ex:
    itemcnt.error("Error encountered!")
    debugcnt.write(ex)
