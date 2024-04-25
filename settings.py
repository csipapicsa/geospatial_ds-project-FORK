import streamlit as st


def settings_page_init():
    st.write("Settings page")
    # slider between 1 and 40
    st.session_state.number_of_forest_areas = st.slider("Number of extra forest areas to be visited: ", 1, 40, st.session_state.get("number_of_forest_areas", 5))
    st.session_state.bikelane_buffer = st.slider("Searching radius around the bike lane (meter)", 100, 1000, st.session_state.get("bikelane_buffer", 500))