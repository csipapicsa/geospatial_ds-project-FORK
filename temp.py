import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium
from functions import get_routes_from_coordinates, routes_to_gdf
import streamlit_functions as stf

def main():
    if 'map' not in st.session_state:
    # Initialize the map and save it in the session state
        st.session_state.map = folium.Map(location=[56.2639, 10.5018], zoom_start=7)
        Draw(export=True).add_to(st.session_state.map)

    # Display the map
        st.session_state.output = st_folium(st.session_state.map, width=700, height=500, key="map")

    if st.button("Calculate"):
        # Process drawing output and prepare for shortest path calculation
        st.session_state.cleaned_output_wgs, cleaned_output_denmark_crs = stf.get_points_from_draw(st.session_state.output)
        st.session_state.validator, result_wgs, result_dk = stf.get_points_validator_2(st.session_state.output)

        st.write("Points are (WGS84): ")
        st.markdown(st.session_state.cleaned_output_wgs)
        st.write("Points are (EPSG:25832): ")
        st.markdown(cleaned_output_denmark_crs)

        if st.session_state.validator:
            if st.button("Show me shortest path"):
                st.session_state.shortest_path_df = routes_to_gdf(get_routes_from_coordinates(st.session_state.cleaned_output_wgs))
                lat, lon = st.session_state.shortest_path_df.geometry.centroid.iloc[0].y, st.session_state.shortest_path_df.geometry.centroid.iloc[0].x
                st.session_state.map_2 = stf.gdf_to_folium_map(st.session_state.shortest_path_df, lat, lon)
                st_folium(st.session_state.map_2, width=700, height=500, key="map_2")

if __name__ == "__main__":
    main()