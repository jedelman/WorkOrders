import streamlit as st
import db
import geopandas as gpd

def refresh_civic_leagues():
    yield("getting civic leagues\n\n")
    civic_leagues = db.get_civic_leagues_from_local_file()
    yield(f"got {len(civic_leagues)} leagues\n\n")

    yield("uploading.\n\n")
    civic_leagues.to_postgis(db.DB_NAMES.CIVIC_LEAGUES, db.engine)
    yield("success!\n\n")

def refresh_addresses():
    yield("getting addresses\n\n")
    addresses = gpd.GeoDataFrame(db.get_addresses_from_local_db())
    yield(f"got {len(addresses)} addressess\n\n")

    yield("writing addresses\n\n")
    addresses.to_postgis('norfolk_addresses', db.engine)
    yield(f"wrote {len(addresses)} addresses\n\n")

def refresh_postgis_mynorfolk():
    yield("getting mynorfolk data\n\n")
    mnf = db.get_mnf_from_socrata()
    yield(f"got {len(mnf)} rows\n\n")

    yield("success! uploading...\n\n")
    mnf.to_sql('mynorfolk', db.engine)
    yield("upload complete!\n\n")

def refresh_complaints():
    yield("getting complaints...\n\n")
    complaints = db.get_complaints_from_local_db()
    yield(f"got {len(complaints)} \n\n")

    yield("uploading complaints \n\n")
    complaints.to_sql(name='complaints', con=db.engine)
    yield("success! \n\n")


if not st.user.is_logged_in:
    if st.button("Login"):
        st.login()
else:
    if st.user.to_dict()['email'] == st.secrets['admin_user']:
        if st.button("refresh addresses"):
            st.write_stream(refresh_addresses())

        if st.button("refresh-mynorfolk") :
            st.write_stream(refresh_postgis_mynorfolk())

        if st.button("refresh-civic-leagues"):
            st.write_stream(refresh_civic_leagues())

        if st.button("refresh complaints"):    
            st.write_stream(refresh_complaints())
    
    if st.button("Log Out"):
        st.logout()
