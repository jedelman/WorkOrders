import streamlit as st
import altair as alt
from datetime import datetime
from db import get_complaints_from_local_db, get_mnf_from_local_db, get_work_orders_from_local_db


st.set_page_config(page_title="City complaint analysis", layout="wide")

addr_filter = st.text_input(label="address filter", value="warren cres")

count = "count()"

class complaint_columns:
    complaint_id = "complaint_id"
    gpin = "gpin"
    address = "address"
    latitude, longitude = "latitude:Q", "longitude:Q"
    ward, superward = "ward", "superward"
    created_date = "created_date"
    last_modified_date =   "last_modified_date"
    closed_date = "closed_date"
    origin = "origin"
    status = "status"
    complaint_type = "complaint_type"
    subtype = "subtype"
    create_inspection = "create_inspection"
    department_responsible = "department_responsible"

class mnf_columns:
    service_request_number = "service_request_number"
    service_request_category = "service_request_category"
    service_request_type = "service_request_type"
    status = "status"
    location = "location"
    creation_date = "creation_date"
    modification_date = "modification_date"


complaint_query = ''
mnf_query = ''
wo_query = ''

if(addr_filter != ''):
    complaint_query += f'address.str.contains("{addr_filter}", case=False, na=False)'
    mnf_query += f'location.str.contains("{addr_filter}", case=False, na=False)'
    wo_query += f'street.str.contains("{addr_filter}", case=False, na=False) or civic_league.str.contains("{addr_filter}", case=False, na=False)'


complaints = get_complaints_from_local_db(complaint_query)
mnf_entries = get_mnf_from_local_db(mnf_query)
complaints = complaints.rename(columns={'type': complaint_columns.complaint_type})

chart = alt.Chart(complaints)
intervalselect = alt.selection_interval()

chart = chart.mark_circle().encode(
    alt.Row(complaint_columns.complaint_type),
    alt.Y(complaint_columns.subtype).title(None),
    alt.Color(complaint_columns.subtype).scale(scheme='accent').legend(orient='bottom', columns=3),
    alt.X('created_date:T').scale(nice='year'),
    alt.Tooltip(["created_date:T", 
                 "last_modified_date:T", 
                 complaint_columns.complaint_type, 
                 complaint_columns.subtype, 
                 complaint_columns.address, 
                 complaint_columns.origin])
    ).properties(bounds='flush')

chart = chart.resolve_scale(y='independent').resolve_axis(y='independent')

mnfchart = alt.Chart(mnf_entries)

mnfchart = mnfchart.mark_circle().encode(
    alt.Row(mnf_columns.service_request_category),
    alt.Y(mnf_columns.service_request_type),
    alt.X(f"{mnf_columns.creation_date}:T"),
    alt.Color(mnf_columns.service_request_type),
    alt.Tooltip([
        mnf_columns.service_request_number,
        mnf_columns.status,
        mnf_columns.service_request_category,
        mnf_columns.service_request_type,
        f"{mnf_columns.creation_date}:T",
        mnf_columns.location,

    ])
).properties(bounds='flush').resolve_scale(y='independent').resolve_axis(y='independent')

wo_items = get_work_orders_from_local_db(wo_query)

wo_chart = alt.Chart(wo_items).mark_circle().encode(
    alt.Row('area:N'),
    alt.Y('problem_description:N'),
    alt.X('start_date:T'),
    alt.Color('primary_task_description:N'),
    alt.Tooltip([
        'area',
        'category_description',
        'problem_description',
        'primary_task_description',
        'start_date:T',
        'created_datetime:T'
    ])
).properties(bounds='flush').resolve_scale(y='independent').resolve_axis(y='independent')

"complaints"
st.altair_chart(chart)

"mynorfolk requests"
st.altair_chart(mnfchart)

"work orders"
st.altair_chart(wo_chart)

