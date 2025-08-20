import streamlit as st
import altair as alt
import re
from altair import datum 
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
                 hide_index=True,
                 column_order=columns,
                 column_config=column_config,
                 selection_mode="multi-column",
                 on_select="rerun"
    )

def timeline(items):
    encodings = [alt.Row('area'), alt.Color('area')]
    colSelect = []
    try:
        colSelect = st.session_state["items"]["selection"]["columns"]
        match len(colSelect):
            case 1: 
                encodings = [alt.Row(f'{colSelect[0]}:N')]
            case 2:
                encodings = [
                    alt.Row(f'{colSelect[0]}:N'),
                    alt.Y(f'{colSelect[1]}:N')
                ]
            case 3:
                encodings = [
                    alt.Row(f'{colSelect[0]}:N'),
                    alt.Y(f'{colSelect[1]}:N'),
                    alt.YOffset(f'{colSelect[2]}:N')
                ]
            case 4:
                encodings = [
                    alt.Row(f'{colSelect[0]}:N'),
                    alt.Y(f'{colSelect[1]}:N'),
                    alt.YOffset(f'{colSelect[2]}:N'),
                    alt.Color(f'{colSelect[3]}:N')
                ]
            case default:
                None
    except KeyError:
        None
    except IndexError:
        None

    def dateChart(items):
        return alt.Chart(items).mark_circle().encode(
            alt.X('start_date:T'),
            alt.Size('count()').scale(scheme='turbo'),
            *encodings
        ).properties(
            title='Start Date (click and drag to select)', height=50, bounds="flush"
        ).resolve_scale(
            y='independent'
        ).add_params(
            alt.selection_interval(encodings=['x'], name='timeframe'), alt.selection_point(name='category'))
    
    def timeline_select():
        start_date = "start_date"

        if 'timeline' in st.session_state:
            selection = st.session_state['timeline']['selection']
            
            if 'timeframe' in selection:
                timeframe_result = selection['timeframe']
                        
                if start_date in timeframe_result:
                    if(len(timeframe_result[start_date]) == 2):
                        start, end = timeframe_result[start_date]
                        start /= 1000
                        end /= 1000
                        st.session_state['dates'] = [
                                datetime.fromtimestamp(start), datetime.fromtimestamp(end)
                                ]
                

            if 'category' in selection:
                st.write(selection)
                for item in selection['category']:
                    for idx, key in enumerate(item):
                        if not start_date == key:
                            st.session_state[SEARCH_QUERY] |= {key:item[key]}

    st.altair_chart(dateChart(items), key='timeline', on_select=timeline_select)
    

def showQuery(container):
    if('dates' in st.session_state):
        container.write("current search filters. click to remove.")
        [start, end] = st.session_state.dates
        if(container.button(f"dates: {start:%Y-%m-%d} - {end:%Y-%m-%d}")):
            del st.session_state.dates
            st.rerun()
    else:
        container.write('showing all dates.')
        container.write("current search filters. click to remove.")

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
    
    items = get_work_orders_from_local_db(buildQuery())
    
    st.metric("Work orders", value=items.index.size)
    
    """
    The currently selected items are displayed below. Click on a column to chart it in the timelines. Ctrl-click to chart multiple columns.
    """

    display_items(items)

    """
    The selected columns are charted below. Click and drag to select a timeframe. Click on a circle to filter.
    """

    f"""
    currently filtered to: **{civic_leagues}**

    explore using the filters below.

    """

    showQuery(st)

    timeline(items)
   

except Exception as ex:
    ex
