import streamlit as st

page = st.navigation(position="sidebar", pages={
    "Work Orders":[
        st.Page("statsonly.py", title="Work Orders Stats"),
        st.Page("orders-search.py", default=True, title="Work Orders Search"),
        st.Page("order-detail.py", title="Work Order Detail")
    ],
    "Expenditures":[
        st.Page("expenditures.py", title="Expenditures")
    ],
    "Maps":[
        st.Page("civic_leagues.py", title="Civic Leagues"),
        st.Page("trees.py", title="Trees")
    ]
})


if 'selected_civic_league' in st.session_state:
    st.sidebar.page_link(page="civic_leagues.py", label=st.session_state['selected_civic_league'])
    page.run()

else:
    if not 'map_forced' in st.session_state:
        st.session_state['map_forced'] = True
        st.switch_page("civic_leagues.py")
    else:
        del st.session_state['map_forced']
        page.run()
