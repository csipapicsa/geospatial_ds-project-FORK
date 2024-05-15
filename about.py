import streamlit as st

def about_page_init():
    st.title("About")
    st.markdown("""
    This is a project for the course 'Geospatial Data Science' at the University of Copenhagen, spring semester 2024. 
    The goal of the project is to create a web-based application that allows the user to find the shortest path between two points on the map and 
    maximize the number of forest areas along this path.
    """)
    st.divider()

    st.title("Contributors")
    st.markdown("""
    - Gergo Gyori (email: gergo.gyori@gmail.com)
    - Gino Fazzi (email: gifa@itu.dk)
    - Jacob Rohde (email: jacro@itu.dk)
    """)
    st.divider()

    st.title("Limitations of the Project")
    st.markdown("""
    The shortest path algorithm relies on the OpenRouteService API due to the limitations of the project. 
    The OpenRouteService API has a limit of 40 requests per minute and 2500 requests per day. 
    If the limit is exceeded, the application will not work.

    The API does not allow adding more than 2 extra points if the shortest path algorithm is set to bike-mountain. 
    Therefore, we have to use the bike-regular option, which prioritizes biking on normal roads.
    This is why the app tends to give back the shortest path which, instead of going through the forest area, makes a detour. 
    With the shortest path algorithm relying on our logic, the shortest path goes through forest areas instead of making detours.

    The application will not work if the limit is exceeded.
    """)