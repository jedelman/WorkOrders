import streamlit as st

def render_work_order(container, row):
    rowcnt, debugrowcnt = container.tabs(["work order", "raw data"])
    rowid = row["work_order_number"]
    debugrowcnt.write(row)
    rowcnt.link_button(row.get("work_order_number"), f"/order-detail?work_order_number={rowid}")
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
