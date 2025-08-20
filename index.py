import streamlit as st
cltitle = f"Civic League Select ({st.session_state['selected_civic_league']})" if 'selected_civic_league' in st.session_state else "Select Civic League"

page = st.navigation(position="sidebar", pages=[
        st.Page("orders-search.py", title="Work Orders"),
        st.Page("civic_leagues.py", default=True, title=cltitle),
        st.Page("combinedmap.py", title="Map"),
        st.Page("admin.py", title="admin")
    ])


if 'selected_civic_league' in st.session_state:
    page.run()

else:
    if not 'map_forced' in st.session_state:
        st.session_state['map_forced'] = True
        st.switch_page("civic_leagues.py")
    else:
        del st.session_state['map_forced']
        page.run()
