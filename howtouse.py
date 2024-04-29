import streamlit as st

def howtouse_page_init():
    st.write("#### 1. Choose two points (your starting point and destination) on the map")
    # add image
    st.image("images/howto_1.png")
    st.write("#### 2. Click on the 'Calculate' button")
    st.write("Points should be valid. It means you have to draw exactly two points on the map")
    st.image("images/howto_2.png")
    # add image
    st.write("#### 3. The shortest path will be shown on the map")
    # add image
    st.image("images/howto_3.png")

    st.write("#### 4. Maximising the visited forest area")
    st.write("Based on your settings in the next round the algorithm will try to maximise the visited forest area")
    st.image("images/howto_4.png")
    st.image("images/howto_5.png")

    st.write("#### 4. On the bottom of the page you can see the statistics of the shortest path")
    st.image("images/howto_6.png")