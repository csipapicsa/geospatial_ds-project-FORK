import streamlit as st
import functions as f
from streamlit_functions import geodataframe_to_map_converter, visualize_geodata, initFoliumMap
import geopandas as gpd
from streamlit_folium import folium_static

def main():
    st.title("Test page")
    st.write("This is a demo of Streamlit")

    st.session_state["number_of_elements"] = 100#st.slider("Number of elements in the forest and bikelane dataset", 0, 100000, 1)
    st.warning("Data is schuffled before visualization.")
    st.write(st.session_state["number_of_elements"])

    if st.button("Show a test map"):
        """
        gdf = f.open_layer_from_db(database_name='test_database.db',
                     table_name='test',
                     crs = f.CRS)

        st.map(geodataframe_to_map_converter(gdf))
        """

        st.write("**Groceries, supermarkets*")

        gdf = gpd.read_parquet("dataset/raw_unprocessed/grocery.parquet")  # Load your GeoDataFrame

        st_map2 = folium_static(initFoliumMap(gdf))
        
        st.write("**Forest areas**")
        st.write("Data is shuffled before visualization")
        # Example usage
        gdf_2 = gpd.read_parquet("dataset/raw_unprocessed/forest_simplified.parquet")  # Load your GeoDataFrame
        gdf_2 = gdf_2.sample(frac=1).reset_index(drop=True)
        st_map2 = folium_static(initFoliumMap(gdf_2, number_of_elements=st.session_state["number_of_elements"]))

        st.write("**Bike lanes**")
        st.write("Data is shuffled before visualization")
        #st.error("Query parameters are obviusly wrong, but this is just a demo")
        gdf_3 = gpd.read_parquet("dataset/raw_unprocessed/bikelane_dk.parquet")  # Load your GeoDataFrame
        # shuffle the data
        gdf_3 = gdf_3.sample(frac=1).reset_index(drop=True)
        st_map3 = folium_static(initFoliumMap(gdf_3, number_of_elements=st.session_state["number_of_elements"]))

main()