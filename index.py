import streamlit as st

page = st.navigation(position="top", pages={
    "Work Orders":[
        st.Page("statsonly.py", title="Work Orders Stats"),
        st.Page("orders-search.py", title="Work Orders Search"),
    ],
    "Complaints":[
        st.Page("complaints.py", title="Complaints"),
    ]
})

page.run()