import streamlit as st
import altair as alt
import re
from db import get_work_orders_from_local_db, buildQuery
from datetime import datetime, timedelta
from render_work_order import render_work_order

civic_leagues = re.sub(' and |,', '/ ', st.session_state["selected_civic_league"])

f"""
# Work Orders Search
"""

SEARCH_QUERY = "search_query"

if SEARCH_QUERY not in st.session_state:
    st.session_state[SEARCH_QUERY] = {} # clauses

def display_items(items):
    if items is None or len(items) == 0:
        return "nothing to show"

    columns = ["area",
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
    encodings = [
        alt.Color('area'),
        ]
    colSelect = []
    try:
        colSelect = st.session_state["items"]["selection"]["columns"]
        if len(colSelect) > 0:
            encodings.append(alt.Y(f'{colSelect[0]}:N').sort('-size'))
        else:
            encodings.append(alt.Y('area:N'))
    except KeyError:
        print("key error")
    except IndexError:
        print("index error")

    def dateChart(items):
        return alt.Chart(items).mark_circle().encode(
            alt.X('start_date:T'),
            alt.X2('status_datetime:T'),
            alt.Size('sum(total_cost):Q'),
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
    if('dates' in st.session_state):
        container.write("current search filters. click to remove.")
        [start, end] = st.session_state.dates
        if(container.button(f"dates: {start:%Y-%m-%d} - {end:%Y-%m-%d}")):
            del st.session_state.dates
            st.rerun()

    search = st.session_state[SEARCH_QUERY]
    
    if(len(search) < 1): return
    container.write("current search filters. click to remove.")

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
    
    items = get_work_orders_from_local_db(buildQuery())
    
    st.metric("Work orders", value=items.index.size)


    f"""
    currently filtered to: **{civic_leagues}**

    """

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
