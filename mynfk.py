import streamlit as st
import altair as alt
from db import get_mnf_from_local_db, get_addresses_from_local_db

st.set_page_config(page_title="MyNorfolk request analysis", layout="wide")

locfilter = st.text_input("Location filter")

items = get_mnf_from_local_db(f"service_request_category == 'Parks & Urban Forestry' and location.str.contains('{locfilter}', case=False)")
addresses = get_addresses_from_local_db()

service_request_number = "service_request_number"
service_request_category = "service_request_category"
service_request_type = "service_request_type"
status = "status"
location = "location"
creation_date = "creation_date"
modification_date = "modification_date"
count = "count()"

base = alt.Chart(items)

type_select = alt.selection_point(fields=[service_request_type], bind="legend", empty=False)
date_select = alt.selection_interval(encodings=['x'])

category_chart = base.mark_rect().encode(
    alt.Y("service_request_type:N"),
    alt.X(count),
    alt.Tooltip([service_request_type])
).resolve_scale(y='independent').add_params(
        type_select)

time_chart = base.mark_tick().encode(
    alt.X("creation_date:T").scale(nice='month'),
    alt.Color(service_request_type),
    alt.Y(service_request_type),
    alt.Tooltip([creation_date, modification_date, location])
).add_params(date_select, type_select)

detail = time_chart.transform_filter(type_select, date_select)

st.altair_chart(time_chart & detail)

