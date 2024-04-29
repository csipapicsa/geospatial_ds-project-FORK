import streamlit as st
from functions import DENMARK_CRS

def statistics_page_init():
    if "shortest_path_df_wgs84" in st.session_state:
        if st.session_state.shortest_path_df_wgs84 is not None:
            st.session_state.shortest_path_df_dk = st.session_state.shortest_path_df_wgs84.to_crs(DENMARK_CRS)
            st.write("Length of the original road is:")
            st.write(f"{st.session_state.shortest_path_df_dk.length.sum() / 1000:.2f} km")
    else:
        st.write("No road has been calculated")

    if "shortest_path_df_2_wgs84" in st.session_state:
        if st.session_state.shortest_path_df_2_wgs84 is not None:
            st.session_state.shortest_path_df_2_dk = st.session_state.shortest_path_df_2_wgs84.to_crs(DENMARK_CRS)
            st.write("Length of the second road is:")
            st.write(f"{st.session_state.shortest_path_df_2_dk.length.sum() / 1000:.2f} km")

    