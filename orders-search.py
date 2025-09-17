import streamlit as st
import altair as alt
import re
from db import get_work_orders_from_local_db, buildQuery, work_orders_fulltext_search
from datetime import datetime, timedelta
from render_work_order import render_work_order

st.set_page_config(layout='wide', menu_items={"Report a Bug":"https://github.com/jedelman/WorkOrders/issues/new/choose"})


civic_leagues = re.sub(' and |,', '/ ', "Ghent Neighborhood League") #hardcoded for demo

f"""
# Work Orders Search
"""



SEARCH_QUERY = "search_query"

if SEARCH_QUERY not in st.session_state:
    st.session_state[SEARCH_QUERY] = {} # clauses

def display_items(items):
    if items is None or len(items) == 0:
        return "nothing to show"

    columns = ["work_order_number",
                "area",
                "category_description", 
                'problem_description',
                "primary_task_description",
                "total_cost",
                "priority",
                "street",
                "status_description",
                "status_datetime",
                "start_date",
                "created_datetime"]

    column_config = {
        "work_order_number": st.column_config.TextColumn("Work Order Number"),
        "area": st.column_config.TextColumn("Area"),
        "category_description":st.column_config.TextColumn("Category"), 
        'problem_description':st.column_config.TextColumn("Problem"),
        "primary_task_description":st.column_config.TextColumn("Primary Task"),
        "total_cost":st.column_config.NumberColumn("Total Cost", format="dollar"),
        "street":st.column_config.TextColumn("Street"),
        "priority":st.column_config.TextColumn("Priority"),
        "status_description":st.column_config.TextColumn("Status"),
        "status_datetime":st.column_config.DatetimeColumn("Status As Of", format="localized"),
        "start_date":st.column_config.DateColumn("Started On", format="localized"),
        "created_datetime":st.column_config.DatetimeColumn("Created At", format="localized")
        }
    
    st.dataframe(data=items,
                 key="items", 
                 use_container_width=True,
                 column_order=columns,
                 column_config=column_config,
                 selection_mode="single-column",
                 on_select="rerun"
    )

def timeline(items):
    encodings = [alt.Y('area:N').sort('-size'), alt.Color('area:N')]
    try:
        colSelect = st.session_state["items"]["selection"]["columns"]
        encodings = [alt.Y(f'{colSelect[0]}:N').sort('-size'),
                     alt.Color(f'{colSelect[0]}:N')]
    except KeyError:
        print("key error")
    except IndexError:
        print("index error")

    def dateChart(items):
        return alt.Chart(items).mark_circle().encode(
            alt.X('start_date:T').scale(nice="year"),
            alt.X2('status_datetime:T'),
            alt.Size('sum(total_cost):Q'),
            alt.Tooltip(['work_order_number', 'total_cost', 'start_date:T', 'area', 'problem_description', 'primary_task_description']),
            *encodings
        ).properties(
            title='Start Date (click and drag to select)'
        ).resolve_scale(
            y='independent'
        ).add_params(
            alt.selection_interval(encodings=['x','y'], name='timeframe'))
    
    def timeline_select():
        start_date = "start_date"
        if 'timeline' in st.session_state:
            selection = st.session_state['timeline']['selection']
            
            if 'timeframe' in selection:
                timeframe_result = selection['timeframe']

                for idx, key in enumerate(timeframe_result):
                    if not start_date == key:
                        item = timeframe_result[key]
                        st.session_state[SEARCH_QUERY] |= {key:item}
                    else:
                        if(len(timeframe_result[start_date]) == 2):
                            start, end = timeframe_result[start_date]
                            start /= 1000
                            end /= 1000
                            st.session_state['dates'] = [
                                    datetime.fromtimestamp(start), datetime.fromtimestamp(end)
                                    ]

    st.altair_chart(dateChart(items), key='timeline', on_select=timeline_select)
    

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
        


try:
    query = st.text_input("full text search", key="query", width="stretch")

    filter = buildQuery()

    if query != '':
        items = work_orders_fulltext_search(query, filter)
    else:
        items = get_work_orders_from_local_db(filter)
    
    col1, col2 = st.columns(2)
    col1.metric("Work orders", value=items.index.size)
    col2.metric("Total Cost", value=f"${items["total_cost"].map(float).sum():,.2f}")


    showQuery(st)

    """
    The work orders are charted below. Bubble size indicates cost. Click and drag to select.
    """

    timeline(items)

    """
    The currently displayed items are listed below. Click on a column to chart it in the timelines.
    """

    display_items(items)

   

except Exception as ex:
    ex
