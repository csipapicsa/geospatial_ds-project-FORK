import streamlit as st


def settings_page_init():
    st.write("Settings page")
    # slider between 1 and 40

    

    # st.session_state.number_of_forest_areas = st.slider("Number of extra forest areas to be visited: ", 0, st.session_state.max_forest_area, st.session_state.get("number_of_forest_areas", 5))
    # Slider for selecting number of extra forest areas
    st.session_state.number_of_forest_areas = st.slider(
        "Number of extra green areas to be visited: ",
        0,
        st.session_state.max_forest_area,
        st.session_state.number_of_forest_areas_new
    )

    if st.session_state.number_of_forest_areas != st.session_state.number_of_forest_areas_new:
        st.session_state.number_of_forest_areas_new = st.session_state.number_of_forest_areas

    # Slider for adjusting bikelane buffer
    st.session_state.bikelane_buffer = st.slider(
        "Searching radius around the bike lane (meter)",
        100,
        2000,
        st.session_state.bikelane_buffer_new
    )

    if st.session_state.bikelane_buffer != st.session_state.bikelane_buffer_new:
        st.session_state.bikelane_buffer_new = st.session_state.bikelane_buffer