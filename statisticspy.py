import streamlit as st
from functions import DENMARK_CRS

def statistics_page_init():
    st.session_state.stat_on = True
    if "shortest_path_df_wgs84" in st.session_state:
        if st.session_state.shortest_path_df_wgs84 is not None:
            st.session_state.shortest_path_df_dk = st.session_state.shortest_path_df_wgs84.to_crs(DENMARK_CRS)
            st.write("Length of the shortest path is:")
            st.write(f"{st.session_state.shortest_path_df_dk.length.sum() / 1000:.2f} km")
            if st.session_state.no_forest_areas_along_the_path:
                st.write("No green area has been crossed by the path")
            else:
                st.write("Total length of the road across green areas is:")
                st.write(f"{st.session_state.shortest_path_1_line_segments_across_forest_dk.length.sum() / 1000:.2f} km")
                st.write("Percentage of the green area:")
                st.write(f"{st.session_state.shortest_path_1_line_segments_across_forest_dk.length.sum() / st.session_state.shortest_path_df_dk.length.sum() * 100:.2f} %")
    else:
        st.write("No road has been calculated")
    # add a separator 
    st.divider()

    if "shortest_path_df_2_wgs84" in st.session_state:
        if st.session_state.shortest_path_df_2_wgs84 is not None:
            st.session_state.shortest_path_df_2_dk = st.session_state.shortest_path_df_2_wgs84.to_crs(DENMARK_CRS)
            st.write("Length of the second path is:")
            st.write(f"{st.session_state.shortest_path_df_2_dk.length.sum() / 1000:.2f} km")
            if st.session_state.shortest_path_2_line_segments_across_forest_dk.empty:
                st.write("No green area has been crossed by the path")
            else:
                st.write("Total length of the road across green areas is:")
                st.write(f"{st.session_state.shortest_path_2_line_segments_across_forest_dk.length.sum() / 1000:.2f} km")
                st.write("Percentage of the green area:")
                st.write(f"{st.session_state.shortest_path_2_line_segments_across_forest_dk.length.sum() / st.session_state.shortest_path_df_2_dk.length.sum() * 100:.2f} %")

    