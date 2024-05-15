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
from functions import get_routes_from_coordinates, routes_to_gdf, DENMARK_CRS, get_only_areas_which_are_crossed_by_bikelane
import functions as f
from statisticspy import statistics_page_init


DEBUG = False
DEBUG_2 = False

st.session_state.draw = Draw(export=True)

def draw_page_init():

    st.write("## Pick up two points")
    st.write("""1. Pick up two points on the map by choosing clicking on the map. 
             These points represents the start and the end of the route.""")


    bounds = [
        [57.751949, 8.085938],  # Northwest corner of Denmark
        [54.559322, 12.832031]  # Southeast corner of Denmark
    ]

    st.session_state.ma = folium.Map(location=[56.2639, 10.5018], zoom_start=7, width=700, height=1000)
            # m.fit_bounds(bounds)
            # m = folium.Map(location=[54.2639, 12.5018], zoom_start=6)
    Draw(export=False).add_to(st.session_state.ma)

    st.session_state.output_new = st_folium(st.session_state.ma , key="base_map", height=1000, width=1000)   

    """
    
    if not st.session_state.output_new and st.session_state.output_old != []:
        st.session_state.output_actual = st.session_state.output_old
    else:    
        if st.session_state.output_new != st.session_state.output_old:
            st.session_state.output_actual = st.session_state.output_new
    """
    st.session_state.output_actual = st.session_state.output_new



    if st.button("Validate", type="primary"):
        st.session_state.phase_2 = False
        st.session_state.cleaned_output_wgs, cleaned_output_denmark_crs = stf.get_points_from_draw(st.session_state.output_actual, method="draw")
        st.session_state.validator, result_wgs, result_dk = stf.get_points_validator_2(st.session_state.output_actual)
        st.write("Points are (WGS84): ")
        st.markdown(st.session_state.cleaned_output_wgs)
        #st.write("Points are (EPSG:25832): ")
        #st.markdown(cleaned_output_denmark_crs)
        if st.session_state.validator:
            st.session_state.phase_2 = True

    if DEBUG:
        coordinates1 = [[11.581726, 55.606109], [11.699829, 55.592143]]
        st.session_state.cleaned_output_wgs, cleaned_output_denmark_crs = stf.get_points_from_draw(coordinates1, method="debug")
        st.session_state.validator, result_wgs, result_dk = stf.get_points_validator_2(st.session_state.output_actual)
        st.session_state.phase_2 = True


    if st.session_state.get("phase_2", False):
        if st.button("Show me the shortest path", type="primary"):
            # Create a Folium Map object
            map_2 = folium.Map()
            st.session_state.shortest_path_df_wgs84 = routes_to_gdf(get_routes_from_coordinates(st.session_state.cleaned_output_wgs, 350, call="streamlit", mode=st.session_state.bike_mode_new))
            lat, lon = st.session_state.shortest_path_df_wgs84.geometry.centroid.iloc[0].y, st.session_state.shortest_path_df_wgs84.geometry.centroid.iloc[0].x
            shortest_path_1 = stf.gdf_to_folium_map(st.session_state.shortest_path_df_wgs84, lat, lon)
            # Add the GeoDataFrame features to the map
            folium.GeoJson(st.session_state.shortest_path_df_wgs84).add_to(map_2)
            #map_2 = folium_static(shortest_path_1 , width=700, height=500)
            # Get the bounds of the features in the GeoDataFrame
            bounds = st.session_state.shortest_path_df_wgs84.total_bounds.tolist()
            # Fit the map to the bounds
            map_2.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

            # Display the map
            folium_static(map_2)

            # get already visited forest areas 
            st.session_state.forest_areas_already_in_the_road_wg84 = get_only_areas_which_are_crossed_by_bikelane(st.session_state.forest_areas_with_bikelanes_wgs84, st.session_state.shortest_path_df_wgs84)
            #st.write(" Number of forest areas along the path: ", len(st.session_state.forest_areas_already_in_the_road_wg84))
            st.session_state.forest_areas_already_in_the_road_dk = st.session_state.forest_areas_already_in_the_road_wg84.to_crs(DENMARK_CRS)
            if st.session_state.forest_areas_already_in_the_road_dk.empty:
                st.session_state.no_forest_areas_along_the_path = True
            else:
                st.session_state.shortest_path_1_line_segments_across_forest_dk = st.session_state.shortest_path_df_wgs84.geometry.intersection(st.session_state.forest_areas_already_in_the_road_wg84.geometry.unary_union, align=False).to_crs(f.DENMARK_CRS)

            # move forward
            st.session_state.phase_3 = True

    if DEBUG:
        st.session_state.shortest_path_df_wgs84 = routes_to_gdf(get_routes_from_coordinates(st.session_state.cleaned_output_wgs, 0, call="streamlit", mode=st.session_state.bike_mode_new))
        lat, lon = st.session_state.shortest_path_df_wgs84.geometry.centroid.iloc[0].y, st.session_state.shortest_path_df_wgs84.geometry.centroid.iloc[0].x
        shortest_path_1_wgs84 = stf.gdf_to_folium_map(st.session_state.shortest_path_df_wgs84, lat, lon)
        #map_2 = folium_static(shortest_path_1 , width=700, height=500)
        map_2 = folium_static(shortest_path_1_wgs84)

    # --------------------------------------------------------------------------#
    #                  🌿              GOING THROUGH FOREST   🌲               #
    # --------------------------------------------------------------------------#
    if st.session_state.get("phase_3", False):
        st.write("##### The path, which is going through more green areas")
        BUFFER = st.session_state.bikelane_buffer
        ADD_MORE_AREA_TO_BE_VISITED = st.session_state.number_of_forest_areas

        gdf_routes_dk_crs = st.session_state.shortest_path_df_wgs84.to_crs(f.DENMARK_CRS)
        # reproject forest_areas_already_in_the_road
        gdf_routes_DK_buffered = f.buffer_gdf(gdf_routes_dk_crs, BUFFER)

        # get forest areas along the buffered bikelane
        can_be_reached_forest_areas = f.get_only_areas_which_are_crossed_by_bikelane(st.session_state.forest_areas_with_bikelanes_dk, gdf_routes_DK_buffered)
        st.write("Total green areas can be reached by the actual settings", len(can_be_reached_forest_areas))
        # exttract the already visited forest areas
        indices_to_exclude = st.session_state.forest_areas_already_in_the_road_wg84.index
        # Drop rows from temp dataframe based on indices_to_exclude
        not_visited_forest_areas_dk = can_be_reached_forest_areas.drop(indices_to_exclude)
        # st.write("Extra forest areas: ", len(not_visited_forest_areas_dk))

        # keep only the X biggest ones
        not_visited_forest_areas_dk["area"] = not_visited_forest_areas_dk["geometry"].area
        not_visited_forest_areas_dk.sort_values(by="area", ascending=False, inplace=True)
        try:
            additional_centroids = not_visited_forest_areas_dk.head(ADD_MORE_AREA_TO_BE_VISITED).to_crs(f.CRS).geometry.centroid.to_list()
        except:
            st.session_state.number_of_forest_areas = len(not_visited_forest_areas_dk)
            st.warning(f"There is no {ADD_MORE_AREA_TO_BE_VISITED} pcs of green area to be visited with this parameters. It is reduced to {st.session_state.number_of_forest_areas} pcs.")
            if st.session_state.number_of_forest_areas == 0:
                st.error("There is no green area to be visited. Please try again with different parameters.")
            else:
                additional_centroids = not_visited_forest_areas_dk.head(st.session_state.number_of_forest_areas).to_crs(f.CRS).geometry.centroid.to_list()

        additional_centroids_coordinates = f.list_of_points_to_coordinates(additional_centroids)
        expanded_coordinates = [st.session_state.cleaned_output_wgs[0]] + additional_centroids_coordinates + [st.session_state.cleaned_output_wgs[1]]
        # st.write("All points", len(expanded_coordinates))
        # rerouting
        st.session_state.shortest_path_df_2_wgs84 = routes_to_gdf(get_routes_from_coordinates(expanded_coordinates, BUFFER, call="streamlit", mode=st.session_state.bike_mode_new))
        # map it
        lat, lon = st.session_state.shortest_path_df_2_wgs84.geometry.centroid.iloc[0].y, st.session_state.shortest_path_df_wgs84.geometry.centroid.iloc[0].x
        shortest_path_2 = stf.gdf_to_folium_map(st.session_state.shortest_path_df_2_wgs84, lat, lon)
        #st.session_state.forest_areas_already_in_the_road_2_wg84 = get_only_areas_which_are_crossed_by_bikelane(st.session_state.forest_areas_with_bikelanes_wgs84, st.session_state.shortest_path_df_2_wgs84)

        # get already visited forest areas 
        st.session_state.forest_areas_already_in_the_road_2_wg84 = get_only_areas_which_are_crossed_by_bikelane(st.session_state.forest_areas_with_bikelanes_wgs84, st.session_state.shortest_path_df_2_wgs84)
        st.write(" Number of green areas along the path: ", len(st.session_state.forest_areas_already_in_the_road_2_wg84))
        st.session_state.forest_areas_already_in_the_road_2_dk = st.session_state.forest_areas_already_in_the_road_2_wg84.to_crs(DENMARK_CRS)

        if len(st.session_state.forest_areas_already_in_the_road_2_wg84) == 0:
            st.session_state.shortest_path_2_line_segments_across_forest_dk = []
        else:
            st.session_state.shortest_path_2_line_segments_across_forest_dk = st.session_state.shortest_path_df_2_wgs84.geometry.intersection(st.session_state.forest_areas_already_in_the_road_2_wg84.geometry.unary_union, align=False).to_crs(f.DENMARK_CRS)

        # Create a Folium Map object
        map_3 = folium.Map()
        # Add the GeoDataFrame features to the map
        folium.GeoJson(st.session_state.shortest_path_df_2_wgs84).add_to(map_3)
        
        # Get the bounds of the features in the GeoDataFrame
        bounds_2 = st.session_state.shortest_path_df_2_wgs84.total_bounds.tolist()

        # Fit the map to the bounds
        map_3.fit_bounds([[bounds_2[1], bounds_2[0]], [bounds_2[3], bounds_2[2]]])

        # Display the map
        folium_static(map_3)

        statistics_page_init()


        




