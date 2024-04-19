# --------------------------------------------------------------------------#
#                                   MAIN site                          #
# run from the command line: 'streamlit run streamlit-test-draw-on-map.py'  #
# --------------------------------------------------------------------------#

import streamlit as st
from streamlit_draw import streamlit_draw_page_init
import geopandas as gpd
import functions as f

def main():
    if st.sidebar.button("Draw on map"):
        st.session_state.current_page = "draw"
    if st.sidebar.button("Settings"):
        st.session_state.current_page = "settings"
        None
    if st.sidebar.button("About"):
        st.session_state.current_page = "about"
        None
    if st.sidebar.button("Additonal maps"):
        st.session_state.current_page = "additional"
        None

    if st.session_state.current_page == "draw":
        streamlit_draw_page_init()
    elif st.session_state.current_page == "settings":
        st.write("Settings page")
    elif st.session_state.current_page == "about":
        st.write("About page")
    elif st.session_state.current_page == "additional":
        st.write("Additional maps page")
    elif st.session_state.current_page == "init":
        with st.spinner("Loading..."):
            st.title("Welcome! The page is loading...")
            st.write("Loading some dataset...")
            st.session_state.forest_areas_with_bikelanes = gpd.read_parquet('dataset/processed/forest_areas_with_bikelanes_wgs84_TEMP.parquet')
            # Step 1: Ensure both GeoDataFrames are in the same CRS
            if st.session_state.forest_areas_with_bikelanes.crs != f.DENMARK_CRS:
                st.session_state.forest_areas_with_bikelanes = st.session_state.forest_areas_with_bikelanes.to_crs(f.DENMARK_CRS)
        

    else:
        st.write("No page selected")

if "current_page" not in st.session_state:
    st.session_state.current_page = "init"
main()
