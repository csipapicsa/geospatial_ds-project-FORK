# --------------------------------------------------------------------------#
#                                   DEMO FUNCTION                           #
# run from the command line: 'streamlit run streamlit-test-draw-on-map.py'  #
# --------------------------------------------------------------------------#


import folium
import streamlit as st
from folium.plugins import Draw
import streamlit_functions as stf

from streamlit_folium import st_folium

bounds = [
    [57.751949, 8.085938],  # Northwest corner of Denmark
    [54.559322, 12.832031]  # Southeast corner of Denmark
]

m = folium.Map(location=[56.2639, 10.5018], zoom_start=7)
# m.fit_bounds(bounds)
# m = folium.Map(location=[54.2639, 12.5018], zoom_start=6)
Draw(export=True).add_to(m)

c1, c2 = st.columns([10, 2])
with c1:
    output = st_folium(m)

with c2:
    print(output)
    cleaned_output = stf.get_points_from_draw(output)
    st.write(cleaned_output)