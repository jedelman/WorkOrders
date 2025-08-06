import streamlit as st

def render_work_order(container, row):
    WORK_ORDER_ID = "work_order_number"
    rowid = row[WORK_ORDER_ID]
    v = row.get

    with container:
        if(st.button(rowid, type="primary", use_container_width=True)):
            st.session_state[WORK_ORDER_ID] = rowid
            st.switch_page("order-detail.py")

        st.markdown(f"""

        Street: **{v("street")}**
        
        |Area|Category|Problem|Primary Task|
        |----|--------|-------|------------|
        |{v("area")}|{v("category_description")}|{v('problem_description')}|{v("primary_task_description")}|

        |Total Cost|Priority|Current Status|Started|Created|
        |----------|--------|--------------|-------|-------|
        |{v("total_cost")}|{v("priority")}|{v("status_description")} as of {v("status_datetime_fmt")}||{v("start_date_fmt")}|{v("created_datetime_fmt")}|

        """)

def render_work_order_old(container, row):
    WORK_ORDER_ID = "work_order_number"
    rowcnt, debugrowcnt = container.tabs(["work order", "raw data"])
    rowid = row[WORK_ORDER_ID]
    debugrowcnt.write(row)
    if(rowcnt.button(rowid)):
        st.session_state[WORK_ORDER_ID] = rowid
        st.switch_page("order-detail.py")

    rowcnt.caption("work order number")
    cols = rowcnt.columns(3)
    def setstate(key, newstate):
        st.session_state[key] = newstate

    cat = row.get("category_description")
    cols[0].button(cat, key=f"{rowid}_cat_set", on_click=setstate, args=["category_description", [cat]])
    cols[0].caption("Category")
    cols[1].write(row.get("primary_task_description"))
    cols[1].caption("Action")
    cols[2].write(row.get("total_cost"))
    cols[2].caption("Total Cost")

    cols = rowcnt.columns(3)
    cols[0].write(row.get("created_datetime_fmt"))
    cols[0].caption("Created")
    cols[1].write(row.get("start_date_fmt"))
    cols[1].caption("Started")
    cols[2].write(row.get("status_description"))
    cols[2].write(row.get("status_datetime_fmt"))
    cols[2].caption("Updated")
    

    cols = rowcnt.columns(3)
    cols[0].write(row.get('problem_description'))
    cols[0].caption("Problem")
    cols[1].write(row.get("priority"))
    cols[1].caption("Priority")
    
    cols = rowcnt.columns(3)
    cl = row.get("civic_league")
    if type(cl) is str:
        cols[0].button(cl, key=f"{rowid}_set_cl", on_click=setstate, args=["civic_league", [cl]])
    else:
        cols[0].write(cl)
    cols[0].caption("Civic League")
    cols[1].write(row.get("street"))
    cols[1].caption("Street")
