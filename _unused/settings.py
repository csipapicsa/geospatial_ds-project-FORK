# Bike mode selection
    # st.session_state.bike_mode_new = st.selectbox("Bike mode", ["Regular", "Mountain bike"], index=["Regular", "Mountain bike"].index(st.session_state.bike_mode_new))
    st.write("""
             - In case of mountain bike mode, the maximum number of additional forest areas is set to 1 for long distancies due to the API limitations. However, with this settings the API is tend to generate better results with less detours.
             - In case of regular bike mode, the maximum number of forest areas is set to 40. In this mode the API prefer to avoid dirt roads, therefore detours are more likely to happen.""")


    if st.session_state.bike_mode_new != st.session_state.bike_mode_old:
        if st.session_state.bike_mode_new == "Regular":
            st.session_state.max_forest_area = 40
            st.session_state.bike_mode_old = st.session_state.bike_mode_new
        elif st.session_state.bike_mode_new == "Mountain bike":
            st.session_state.max_forest_area = 4
            st.session_state.bike_mode_old = st.session_state.bike_mode_new
            if st.session_state.number_of_forest_areas_new > st.session_state.max_forest_area:
                st.session_state.number_of_forest_areas_new = st.session_state.max_forest_area

        st.rerun() 