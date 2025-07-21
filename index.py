import streamlit as st

page = st.navigation(position="top", pages={
    "Work Orders":[
        st.Page("statsonly.py", title="Work Orders Stats"),
        st.Page("orders-search.py", title="Work Orders Search"),
        st.Page("order-detail.py", title="Work Order Detail")
    ],
    "Combined Charts":[
        st.Page("combined.py", default=True, title="Combined Charts"),
    ],
    "Expenditures":[
        st.Page("expenditures.py", title="Expenditures")
    ]
})

page.run()