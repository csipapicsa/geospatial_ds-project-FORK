import streamlit as st
import functions as f
from streamlit_functions import geodataframe_to_map_converter

def main():
    st.title("Test page")
    st.write("This is a demo of Streamlit")

    if st.button("Show a test map"):
        gdf = f.open_layer_from_db(database_name='test_database.db',
                     table_name='test',
                     crs = f.CRS)

        st.map(geodataframe_to_map_converter(gdf))

main()

def print():
    print("hello")