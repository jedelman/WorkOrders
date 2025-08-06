import streamlit as st
import altair as alt
from db import get_expenditures_from_local_db

"""
# Budget Browser: Expenditures

the following chart shows current expenditures in the city's budget.
currently it is limited to the current fiscal year.

click on a category to inspect it, and shift-click to inspect multiple categories.

the chart below presents a more detailed breakdown by category.

"""

st.set_page_config(layout="wide")

items = get_expenditures_from_local_db("fiscal_year == 2025")

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
    alt.X("department_name:N").sort("-y").axis(labelAngle=45),
    alt.Color("department_name:N").legend(None),
    opacity=alt.when(deptclick).then(alt.value(0.9)).otherwise(alt.value(0.2))
).add_params(deptclick).properties(
    title="Expenditures"
)


deets = chart.mark_bar(stroke="white").encode(
    alt.X("sum(actual_expenses):Q").stack(True).scale(type="sqrt"),
    alt.Y("unit_name:N").sort("-x"),
    alt.Color("object_name:N").scale(scheme="turbo"),
    alt.Tooltip(['object_name', 
                 'expenditure_category', 
                 'actual_expenses', 
                 'current_expense_budget'])
).transform_filter(deptclick)

fullchart = (piechart & deets)

st.altair_chart(fullchart)
