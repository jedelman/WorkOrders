import streamlit as st
import altair as alt
from db import get_expenditures_from_local_db

items = get_expenditures_from_local_db("fiscal_year == '2025'")

columns = [
"fiscal_year"
"department_name"
"fund_name"
"unit_name"
"expenditure_category"
"object_name"
"actual_expenses"
"current_expense_budget"
]

chart = alt.Chart(items)

deptclick = alt.selection_point(fields=['department_name'])
piechart = chart.mark_bar(
).encode(
    alt.Y("sum(actual_expenses):Q").scale(type="sqrt"),
    alt.X("department_name").sort("-y"),
    alt.Color("department_name:N").legend(None),
    opacity=alt.when(deptclick).then(alt.value(0.9)).otherwise(alt.value(0.2))
).add_params(deptclick)


gridchart = chart.mark_circle().encode(
    alt.Color("department_name"),
    alt.Size('sum(actual_expenses):Q'),
    alt.X("unit_name"),
    alt.Y("expenditure_category"),
    alt.Tooltip(['sum(actual_expenses):Q',
                 'unit_name', 
                 'expenditure_category', 
                 'count()'])
).transform_filter(deptclick)

deets = chart.mark_bar(stroke="white").encode(
    alt.X("sum(actual_expenses):Q").stack(True).scale(type="sqrt"),
    alt.Y("unit_name:N").sort("-x"),
    alt.Color("object_name:N").scale(scheme="turbo"),
    alt.Tooltip(['object_name', 
                 'expenditure_category', 
                 'actual_expenses', 
                 'current_expense_budget'])
).transform_filter(deptclick)


piechart & gridchart & deets