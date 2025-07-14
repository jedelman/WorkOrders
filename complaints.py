import streamlit as st
import altair as alt
from datetime import datetime
from db import get_complaints_from_local_db

st.set_page_config(layout="wide")

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

items = get_complaints_from_local_db('')

items = items.rename(columns={'type': complaint_type})

chart = alt.Chart(items)


chart = chart.mark_area().encode(
    alt.Y('count(type):Q').stack('center'),
    alt.Row(complaint_type),
    alt.Color(subtype).scale(scheme='accent').legend(orient='bottom', columns=3),
    x='yearmonth(created_date):T',
    ).properties(height=50)

chart = chart.resolve_scale(y='independent').resolve_axis(y='independent')

intervalselect = alt.selection_interval(encodings=['x'])
chart = chart.add_params(intervalselect).transform_filter(intervalselect)

categoryselect = alt.selection_point(fields=[complaint_type], bind='legend')
chart = chart.add_params(categoryselect)
chart = chart.transform_filter(categoryselect)


#st.write(items)

st.altair_chart(chart, use_container_width=True)



