import streamlit as st
cltitle = f"Civic League Map ({st.session_state['selected_civic_league']})" if 'selected_civic_league' in st.session_state else "Select Civic League"

st.set_page_config(
    page_icon=":city_sunrise:", 
    layout="wide", 
    menu_items={"Report a Bug":"https://github.com/jedelman/WorkOrders/issues/new/choose"})

if 'selected_civic_league' in st.session_state:
    st.navigation(position="sidebar", pages=[
            st.Page("civic_leagues.py", default=True, title=cltitle),
            st.Page("orders-search.py", title="Work Orders"),
            st.Page("combinedmap.py", title="Map"),
            st.Page("admin.py", title="admin")
        ]).run()
else:
    st.navigation(position="sidebar", pages=[
            st.Page("civic_leagues.py", default=True, title=cltitle)]).run()
    
