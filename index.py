import streamlit as st
cltitle = f"Civic League Select ({st.session_state['selected_civic_league']})" if 'selected_civic_league' in st.session_state else "Select Civic League"

page = st.navigation(position="sidebar", pages={
    "Work Orders":[
        st.Page("statsonly.py", title="Stats"),
        st.Page("orders-search.py", default=True, title="Search"),
    ],
    "Budget Browser":[
        st.Page("expenditures.py", title="Expenditures")
    ],
    "Maps":[
        st.Page("civic_leagues.py", title=cltitle),
        st.Page("complaints.py", title="Complaints"),
        st.Page("mynorfolk.py", title="MyNorfolk Data"),
        st.Page("trees.py", title="Trees")
    ]
})


if 'selected_civic_league' in st.session_state:
    page.run()

else:
    if not 'map_forced' in st.session_state:
        st.session_state['map_forced'] = True
        st.switch_page("civic_leagues.py")
    else:
        del st.session_state['map_forced']
        page.run()
