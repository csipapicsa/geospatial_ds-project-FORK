import streamlit as st


def settings_page_init():
    st.write("Settings page")
    # slider between 1 and 40
    st.session_state.number_of_forest_areas = st.slider("Number of forest areas", 1, 40, st.session_state.get("number_of_forest_areas", 5))
    st.session_state.bikelane_buffer = st.slider("Searching radious around the bikelane", 100, 1000, st.session_state.get("bikelane_buffer", 500))