import folium
from streamlit_folium import folium_static
import streamlit as st

def geodataframe_to_map_converter(gdf):
    """
    Display a geodataframe on a map.
    :param gdf: geodataframe
    :param zoom: zoom level
    :param height: height of the map
    :param width: width of the map
    """
    coordinates = gdf.geometry.centroid
    latitude = coordinates.y  # y-coordinate is latitude
    longitude = coordinates.x  # x-coordinate is longitude
    gdf['latitude'] = latitude
    gdf['longitude'] = longitude

    return gdf

#---------------------------------------------------------------------------------------------#
#                                                                    VISUALIZATION            #
#---------------------------------------------------------------------------------------------#

def visualize_geodata(gdf):
    # this is slow like a shit if the dataset is big 
    # Center the map on the geometric center of the GeoDataFrame
    center = gdf.geometry.centroid.unary_union.centroid.coords[:][0]
    
    # Create a Folium map object
    m = folium.Map(location=center, zoom_start=12)

    # Add geometries from the GeoDataFrame to the map
    for _, row in gdf.iterrows():
        # Simplify geometry for faster rendering
        sim_geo = row.geometry.simplify(tolerance=0.001, preserve_topology=True)
        geo_j = folium.GeoJson(data=sim_geo.__geo_interface__,
                               style_function=lambda x: {'fillColor': 'green', 'color': 'green'})
        geo_j.add_to(m)

    # Display the map in Streamlit
    folium_static(m)


def initFoliumMap(gdf, number_of_elements=[]):
    if number_of_elements != []:
        if number_of_elements > len(gdf):
            st.error(f"Requested number of elements ({number_of_elements}) exceeds the total available in the GeoDataFrame ({len(gdf)}). Please specify a smaller number.")
            raise ValueError(f"Requested number of elements ({number_of_elements}) exceeds the total available in the GeoDataFrame ({len(gdf)}). Please specify a smaller number.")
    layers = {}
    # ma = folium.Map([47, 19.7], zoom_start=7, width='100%')
    ma = folium.Map()
    folium.TileLayer("openstreetmap").add_to(ma)
    layers["Final Result"] = folium.FeatureGroup(name="Final Result")
    if number_of_elements == []:
        ma.add_child(layers["Final Result"].add_child(folium.GeoJson(data=gdf,style_function=lambda x:{'fillColor': "red", 'fillOpacity': 0.5, "opacity": 1, "weight": 2})))
    else:
        ma.add_child(layers["Final Result"].add_child(folium.GeoJson(data=gdf.head(number_of_elements),style_function=lambda x:{'fillColor': "red", 'fillOpacity': 0.5, "opacity": 1, "weight": 2})))
    ma.fit_bounds(ma.get_bounds())

    return ma


# ---------------------------------------------------------------------------------------------#
#                                                                   MAP QUERY                  #
#----------------------------------------------------------------------------------------------#

def get_points_from_draw(input):
    validator, result = get_points_validator_2(input)
    if validator == True:
        st.write(convert_to_coordinate_list(result))
    else:
        st.warning("Please draw only points on the area of Denmark")



def get_points_validator_2(input):
    res = input["all_drawings"]
    points = []
    if type(res) != type(None):
        for item in res:
            print("---- Running")
            #st.write(item["geometry"]["type"])
            #st.write(item["geometry"]["type"] != "Point")
            if item["geometry"]["type"] == "Point":
                coordinates = item["geometry"]["coordinates"][0:2]
                points.append(coordinates)

    print("Coordinates are: ", points)

    if len(points) != 2:
        st.warning("Please pick exactly two points")
        return False, None
    else:
        # is it in Denmark? 
        # 
        return True, points
    

def convert_to_coordinate_list(input_data):
    # Initialize an empty list to hold the converted coordinates
    coordinates = []

    # Iterate through the input data to extract and convert coordinates
    for item in input_data:
        # Each 'item' should be a list containing two elements: longitude and latitude
        if len(item) == 2:
            # Append the coordinate pair to the 'coordinates' list
            coordinates.append([item[0], item[1]])

    return coordinates
