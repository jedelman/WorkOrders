import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import altair as alt
from altair import datum 
from db import get_work_orders_from_local_db
from datetime import datetime, timedelta
from render_work_order import render_work_order

st.set_page_config(
    page_title="Norfolk Work Orders Search", 
    page_icon=":city_sunrise:", 
    layout="wide", 
    menu_items={"Report a Bug":"https://github.com/jedelman/WorkOrders/issues/new/choose"},
    initial_sidebar_state="collapsed")

SEARCH_QUERY = "search_query"

if SEARCH_QUERY not in st.session_state:
    st.session_state[SEARCH_QUERY] = {} # clauses

header = st.container()

itemcnt = st.container()

def areaChart(items):
        return alt.Chart(items).mark_rect().encode(
            alt.Color('area').legend(None),
            alt.Tooltip(['area', 'sum(total_cost)']),
            alt.X('area').stack(True).axis(None),
        ).transform_filter(
            datum.area != None
        ).properties(title="Area", height=100, bounds='flush'
                     ).add_params(
                         alt.selection_point(fields=['area']))

def categoriesChart(items):
    return alt.Chart(items).mark_rect().encode(
        alt.Color('category_description').legend(None),
        alt.X('category_description').stack(True).axis(None)
    ).transform_filter(
        datum.category_description != None
    ).properties(title="Category", height=100
                 ).add_params(
                         alt.selection_point(fields=['category_description']))


param_charts = {
    'area': areaChart,
    'category_description': categoriesChart,
    #'status_description' : nochart,
    #'civic_league': nochart,
    #'street': nochart,
    #'start_date': nochart
}

def display_items(items):
    def datefmt(datestr):
        return datetime.fromisoformat(datestr).strftime("%m/%d/%Y") if type(datestr) is str else None

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

def dateChart(items):
    return alt.Chart(items).mark_rect().encode(
        alt.X('yearmonth(start_date):T').scale(nice='month'),
        alt.Color('count()'),
    ).properties(
        title='Start Date', height=250
    ).add_params(
        alt.selection_interval())

def charts(items, container):
    for (key, chartfunc) in param_charts.items():
        result = container.altair_chart(chartfunc(items), on_select="rerun", use_container_width=True).selection.param_1
        if len(result) > 0 and key in result[0]:
            if key not in st.session_state[SEARCH_QUERY] or st.session_state[SEARCH_QUERY][key] != result[0][key]:
                st.session_state[SEARCH_QUERY][key] = result[0][key]
                st.rerun()

    #date chart
    result = container.altair_chart(dateChart(items), on_select='rerun').selection.param_1
    start_date = "yearmonth_start_date"
    if start_date in result:
        if(len(result[start_date]) == 2):
            start, end = result[start_date]
            start /= 1000
            end /= 1000
            dates = [datetime.fromtimestamp(start), datetime.fromtimestamp(end)]
            if 'dates' not in st.session_state or st.session_state.dates != dates:
                st.session_state.dates = dates
                st.rerun()

            container.write(st.session_state.dates)
        else:
            container.write(result)

def showQuery(container):
    if('dates' in st.session_state):
        [start, end] = st.session_state.dates
        if(container.button(f"{start:%Y-%m-%d} - {end:%Y-%m-%d}")):
            del st.session_state.dates
            st.rerun()

    delkeys = []
    search = st.session_state[SEARCH_QUERY]
    
    if(len(search) < 1): return

    cols = container.columns(len(search))
    
    for idx, key in enumerate(search):
        if(cols[idx].button(f"{key}:{search[key]}")):
            delkeys.append(key)
    
    for key in delkeys:
        del st.session_state[SEARCH_QUERY][key]

def buildQuery():
    return ' and '.join([
        f"{key}.str.contains('{value}', case=False, na=False)"
        for key, value in 
        st.session_state[SEARCH_QUERY].items()])
        

try:
    showQuery(header)

    items = get_work_orders_from_local_db(buildQuery())
    
    header.metric("Work orders", value=items.index.size)
    
    charts(items, header)
    
    if(items.index.size > 0):
        if("page" not in st.session_state):
            st.session_state.page = 0

        def pageview():
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

            prev, perpage, next = itemcnt.columns(3)
            ipp = perpage.selectbox("Items per page", [10,25,50], label_visibility="collapsed")
            startidx, endidx = st.session_state.page*ipp, min((st.session_state.page+1)*ipp, items.index.size)
            prev.button("< Prev", on_click=prevpage, disabled=st.session_state.page==0)
            next.button("Next >", on_click=nextpage, disabled=endidx>=items.index.size-1)
        
            selected = items.iloc[range(startidx, endidx)]

            display_items(selected)

        pageview()

except Exception as ex:
    itemcnt.error("Error encountered!")
    itemcnt.write(ex)
