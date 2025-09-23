import streamlit as st
import altair as alt
import re
import pandas as pd
import db
from db import get_work_orders_from_local_db, buildQuery, work_orders_fulltext_search, get_mnf, get_complaints
from datetime import datetime, timedelta
from render_work_order import render_work_order

st.set_page_config(layout='wide', menu_items={"Report a Bug":"https://github.com/jedelman/WorkOrders/issues/new/choose"})


civic_leagues = re.sub(' and |,', '/ ', "Ghent Neighborhood League") #hardcoded for demo

f"""
### Norfolk Open Data Search
"""


SEARCH_QUERY = "search_query"

if SEARCH_QUERY not in st.session_state:
    st.session_state[SEARCH_QUERY] = {} # clauses


def showQuery(container):
    container.write("current search filters. click to remove.")

    if('dates' in st.session_state):
        [start, end] = st.session_state.dates
        if(container.button(f"dates: {start:%Y-%m-%d} - {end:%Y-%m-%d}")):
            del st.session_state.dates
            st.rerun()

    search = st.session_state[SEARCH_QUERY]
    
    if(len(search) < 1): return

    cols = container.columns(len(search))
    
    def delkey(key):
        del st.session_state[SEARCH_QUERY][key]

    for idx, key in enumerate(search):
        with(cols[idx]):
            st.button(
                label=f"{key}:{search[key]}", 
                key=f'delete_{key}_search', 
                on_click=delkey, 
                kwargs={"key":key})
        

def workorderstab(query, filter):
    items = work_orders_fulltext_search(query, filter)
    col1, col2 = st.columns(2)
    col1.metric("Work orders", value=items.index.size)
    if items.index.size == 0:
        return
    col2.metric("Total Cost", value=f"${items["total_cost"].map(float).sum():,.2f}")

    col1, col2, col3 = st.columns(3)

    colSelect = col1.selectbox("Chart by dimension:", options=items.columns, index=2)
    sizeCol = col2.selectbox("Circle size", options=items.columns, index=22)
    col3.download_button(label="Download Data", data=items.to_csv().encode("utf-8"), file_name="work_orders.csv")
        
    zoom = alt.selection_interval(empty=False)

    basechart = alt.Chart(items).mark_circle().encode(
            alt.X('start_date:T').scale(nice="year"),
            alt.Y(f'{colSelect}:N').sort('-size'),
            alt.Color(f'{colSelect}:N'),
            alt.Size(f'sum({sizeCol}):Q'),
            alt.Tooltip([*items.columns])
        ).properties(
            title='Start Date (click and drag to select)',
        ).add_params(zoom)

    subchart = basechart.transform_filter(zoom).properties(title="Selected Data")

    st.altair_chart(basechart & subchart
    , key='timeline')


def mnftab(query, filter):
    items = get_mnf(query)
    st.metric("MyNorfolk requests", value=items.index.size)

    col1, col2, col3 = st.columns(3)

    colSelect = col1.selectbox("Chart by dimension:", options=items.columns, index=2)
    sizeCol = col2.selectbox("Circle size", options=['count()', *items.columns])
    col3.download_button(label="Download Data", data=items.to_csv().encode("utf-8"), file_name="mynorfolk_requests.csv")

    zoom = alt.selection_interval()

    chart = alt.Chart(items).mark_circle().encode(
            alt.X('yearmonthdate(creation_date):T').scale(nice="year"),
            alt.Size(f'{sizeCol}'),
            alt.Color(f'{colSelect}:N'),
            alt.Y(f'{colSelect}:N'),
            alt.Tooltip([*items.columns])
        ).properties(title="MyNorfolk Requests (click and drag to select)").add_params(zoom)
    
    zoomchart = chart.transform_filter(zoom).properties(title="Selected Requests")

    st.altair_chart(chart & zoomchart)

def complaintstab(query, filter):
    items = get_complaints(query)
    st.metric("Complaints", value=items.index.size)
    st.download_button(label="Download Data", data=items.to_csv().encode("utf-8"), file_name="complaints.csv")
    st.altair_chart(alt.Chart(items).mark_circle(radius=10).encode(
        alt.X('created_date:T').scale(nice="year"),
        alt.Row('type:N'),
        alt.Y('subtype:N'),
        alt.Color('type:N'),
        alt.Tooltip([*items.columns])
    ).properties(title="Complaints"))    

def permitstab(query):
    items = db.permits(query)
    st.metric("Permits", value=items.index.size)
    st.download_button(label="Download Data", data=items.to_csv().encode("utf-8"), file_name="permits.csv")
    colSelect = st.selectbox("Display By:", options=[*items.columns], index=8)
    st.altair_chart(alt.Chart(items).mark_circle(radius=5).encode(
        alt.X('application_date:T').scale(nice="year"),
        alt.Y(f'{colSelect}:N'),
        alt.Color(f'{colSelect}:N'),
        alt.Tooltip([*items.columns])
    ))


def instructions_tab():
    st.markdown(
    """
    # Instructions

    Welcome to [Jason's](https://github.com/jedelman/WorkOrders/) norfolk open data search!

    Use the search bar above to input a query, then select the tabs to see results from Norfolk's datasets.

    Each dataset has a download button to download the serch results in CSV format. This can be imported into Excel or your favorite spreadsheet program.

    To see the underlying data, hover over the chart and click the table icon that pops up in the upper right. This popup menu also gives the option to save the chart as an image.

    Because the datasets are different, each will be charted slightly differently. Click and drag to select subsections of each chart.

    """)

try:
    query = st.text_input("full text search", key="query", width="stretch", placeholder="Please enter a query to search.")

    filter = buildQuery()

    if query != '':
        showQuery(st)
        instr, wo, mnf, comp, permits = st.tabs(["Instructions", "Work Orders", "MyNorfolk Requests", "Complaints", "Permits"])

        with instr:
            instructions_tab()

        with wo:
            workorderstab(query, filter)
        
        with mnf:
            mnftab(query, filter)

        with comp:
            complaintstab(query,filter)

        with permits:
            permitstab(query)


    else:
        instructions_tab()
    

   

except Exception as ex:
    ex
