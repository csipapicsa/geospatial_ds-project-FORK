# --------------------------------------------------------------------------#
#                                   MAIN site                          #
# run from the command line: 'streamlit run streamlit-test-draw-on-map.py'  #
# --------------------------------------------------------------------------#

import streamlit as st

st.set_page_config(
    page_title="Bike & Forest in Denmark",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Project repo: https://github.com/ginofazzi/geospatial_ds-project"
    }
)

from streamlit_draw import draw_page_init
from settings import settings_page_init
from statisticspy import statistics_page_init
from style_functions import local_css
from howtouse import howtouse_page_init
import geopandas as gpd
import functions as f


def main():
    local_css("style.css")
    if st.sidebar.button("Draw on map", type="primary"):
        st.session_state.current_page = "draw"
    if st.sidebar.button("How to use it?", type="primary"):
        st.session_state.current_page = "how_to_page"
    if st.sidebar.button("Settings", type="primary"):
        st.session_state.current_page = "settings"
    if st.sidebar.button("About"):
        st.session_state.current_page = "about"
    if st.sidebar.button("Additonal maps"):
        st.session_state.current_page = "additional"
    if st.sidebar.button("Panic!"):
        # clear session state
        st.session_state.clear()
        st.session_state.number_of_forest_areas = 5
        st.session_state.bikelane_buffer = 500
        st.session_state.current_page = "init"
        st.session_state.phase_1 = True
        local_css("style.css")


    if st.session_state.current_page == "draw":
            # Divide the container into three columns
        #style = "<style>h2 {text-align: center;}</style>"
        #st.markdown(style, unsafe_allow_html=True)
        #col1, col2, col3 = st.columns([1, 8, 1])  # The middle column gets twice the space

        # Use the middle column to display your app's content
        #with col2:
        draw_page_init()  # Call your function to display the map and other elements
    elif st.session_state.current_page == "settings":
        settings_page_init()
    elif st.session_state.current_page == "how_to_page":
        howtouse_page_init()
    elif st.session_state.current_page == "about":
        st.write("About page")
    elif st.session_state.current_page == "additional":
        st.write("Additional maps page")
    elif st.session_state.current_page == "init":
        with st.spinner("Loading..."):
            st.title("Welcome! The page is loading...")
            st.write("Loading some dataset...")
            st.session_state.forest_areas_with_bikelanes_wgs84 = gpd.read_parquet('dataset/processed/forest_areas_crossed_by_bikelane_wgs84.parquet')
            st.session_state.forest_areas_with_bikelanes_dk = gpd.read_parquet('dataset/processed/forest_areas_crossed_by_bikelane_DK.parquet')
            st.session_state.number_of_forest_areas = 5
            st.session_state.bikelane_buffer = 500
        

    else:
        st.write("No page selected")

if "current_page" not in st.session_state:
    st.session_state.current_page = "init"
main()
