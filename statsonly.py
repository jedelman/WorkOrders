from db import get_work_orders_from_local_db
import streamlit as st
import altair as alt
from datetime import datetime

st.set_page_config(layout="wide")

items = get_work_orders_from_local_db("civic_league in ['Ghent Neighborhood League'] and start_date > '2020-01-01'")

chart = alt.Chart(items)

groupby = "area" #"problem_description"
subdivide = "category_description" #"primary_task_description"
measure = "total_cost"

groupbyN, subdivideN = f"{groupby}:N", f"{subdivide}:N", 

startdate, enddate = "min(start_date):T", "max(end_date):T"
summeasure, meanmeasure = f"sum({measure}):Q", f"mean({measure}):Q"
count = "count():Q"

tooltip = [
                "category_description", 
                groupby,
                subdivide,
                startdate,
                enddate,
                summeasure, 
                meanmeasure, 
                count
                ]


timeselect = alt.selection_interval(encodings=['x'])

groupselect = alt.selection_point(fields=['primary_task_description'])

timechart = chart.mark_circle(
).encode(
            alt.Size('total_cost:Q', legend=None).scale(type='sqrt'),
            alt.Y(groupbyN),
            alt.Color(groupbyN).scale(scheme='accent'),
            alt.X("start_date:T").axis(
                tickCount="year"
            ).scale(
                nice='year',
                type='time', 
                rangeMin=0,
                domainMin=datetime(year=2020, month=1, day=1)).timeUnit('yearmonth'),
            
            tooltip=tooltip).add_params(timeselect).resolve_scale(color='independent')


groupchart = chart.mark_bar().encode(
    alt.Y(summeasure).scale(type='quantile'),
    alt.X('area'),
    alt.XOffset('primary_task_description'),
    alt.Color("problem_description:N"),
    alt.Tooltip(['primary_task_description', 'problem_description', summeasure, 'count()']),
    ).transform_filter(timeselect).add_params(groupselect)

detail = groupchart.transform_filter(groupselect).mark_circle().encode(
    alt.Color('count():Q').scale(scheme='rainbow'),
    size='total_cost:Q',
    tooltip=['problem_description','total_cost', 'count()'],
    y='problem_description:N',
    x='yearmonth(start_date):T',
    )

grouplabels = groupchart.mark_text(
    orient='vertical', dy=-15, size=10).encode(
        alt.Size(summeasure).scale(range=[10,10]),
        text='primary_task_description')

groupchart += grouplabels
groupchart.facet(column='area:N').resolve_axis(y='independent')


st.altair_chart(timechart & groupchart)