# --------------------------------------------------------------------------#
#                                   DEMO FUNCTION                           #
# run from the command line: 'streamlit run streamlit-test-draw-on-map.py'  #
# --------------------------------------------------------------------------#


import folium
import streamlit as st
from folium.plugins import Draw
import streamlit_functions as stf
import time

from streamlit_folium import st_folium, folium_static
from functions import get_routes_from_coordinates, routes_to_gdf

DEBUG = True

def streamlit_draw_page_init():
    bounds = [
        [57.751949, 8.085938],  # Northwest corner of Denmark
        [54.559322, 12.832031]  # Southeast corner of Denmark
    ]

    m = folium.Map(location=[56.2639, 10.5018], zoom_start=7)
    # m.fit_bounds(bounds)
    # m = folium.Map(location=[54.2639, 12.5018], zoom_start=6)
    Draw(export=True).add_to(m)

    output = st_folium(m, key="base_map")

    if st.button("Calculate"):
        st.session_state.phase_2 = False
        st.session_state.cleaned_output_wgs, cleaned_output_denmark_crs = stf.get_points_from_draw(output, method="draw")
        st.session_state.validator, result_wgs, result_dk = stf.get_points_validator_2(output)
        st.write("Points are (WGS84): ")
        st.markdown(st.session_state.cleaned_output_wgs)
        st.write("Points are (EPSG:25832): ")
        st.markdown(cleaned_output_denmark_crs)
        st.session_state.phase_1 = False
        if st.session_state.validator:
            st.session_state.phase_2 = True

    if DEBUG:
        coordinates1 = [[11.581726, 55.606109], [11.699829, 55.592143]]
        st.session_state.cleaned_output_wgs, cleaned_output_denmark_crs = stf.get_points_from_draw(coordinates1, method="debug")
        st.session_state.validator, result_wgs, result_dk = stf.get_points_validator_2(output)
        st.session_state.phase_2 = True


    if st.session_state.get("phase_2", False):
        if st.button("Show me shortest path"):
            st.session_state.shortest_path_df = routes_to_gdf(get_routes_from_coordinates(st.session_state.cleaned_output_wgs))
            lat, lon = st.session_state.shortest_path_df.geometry.centroid.iloc[0].y, st.session_state.shortest_path_df.geometry.centroid.iloc[0].x
            shortest_path_1 = stf.gdf_to_folium_map(st.session_state.shortest_path_df, lat, lon)
            #map_2 = folium_static(shortest_path_1 , width=700, height=500)
            map_2 = folium_static(shortest_path_1)
            st.session_state.phase_3 = True

    if DEBUG:
        st.session_state.shortest_path_df = routes_to_gdf(get_routes_from_coordinates(st.session_state.cleaned_output_wgs))
        lat, lon = st.session_state.shortest_path_df.geometry.centroid.iloc[0].y, st.session_state.shortest_path_df.geometry.centroid.iloc[0].x
        shortest_path_1 = stf.gdf_to_folium_map(st.session_state.shortest_path_df, lat, lon)
        #map_2 = folium_static(shortest_path_1 , width=700, height=500)
        map_2 = folium_static(shortest_path_1)


    if st.session_state.get("phase_3", False):
        None


