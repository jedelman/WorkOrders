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

deptselect = alt.selection_point(fields=['department_name'])

piechart = chart.mark_arc().encode(
    alt.Theta("sum(actual_expenses):Q").sort("size"),
    alt.Color("department_name").legend(direction="horizontal", columns=2, orient="top")
).add_params(deptselect)


gridchart = chart.mark_rect().encode(
    alt.Color("sum(actual_expenses):Q"),
    alt.X("unit_name"),
    alt.Y("expenditure_category")
).transform_filter(deptselect)

piechart & gridchart