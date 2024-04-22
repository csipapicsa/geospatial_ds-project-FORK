# ---------------------------------------------------------------- #
#                          IMPORTS - Obviously                     #
# -----------------------------------------------------------------#

import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import Point
import streamlit as st

# database, sql
from sqlalchemy import create_engine
import sqlite3
import subprocess
import os

# maps
import h3
import folium

# services
import openrouteservice

# ---------------------------------------------------------------- #
#                          INIT                                    #
# -----------------------------------------------------------------#

client = openrouteservice.Client(key=st.secrets["OPENROUTSERVICE_API"])

# ---------------------------------------------------------------- #
#                          GLOBAL VARIABLES                        #
# -----------------------------------------------------------------#

TEST_DATABASE = "test_database.db"
DATABASE_RAW = "denmark_raw.db"
DATABASE_CLEAN = "denmark_clean.db"
CRS = "EPSG:4326" # global
DENMARK_CRS = "EPSG:25832"
DENMARK_CRS_INT = 25832
H3_INDEX_RESOLUTION = 6

# ---------------------------------------------------------------- #
#                           MAP RELATED                            #
# -----------------------------------------------------------------#

def save_layer_into_db(gdf, database_name="test_database", table_name="test", if_exists="replace", keep_only_geometry=True):
    """
    Save a geodataframe into a sqlite database.
    :param gdf: geodataframe
    :param database_name: name of the database
    :param table_name: name of the table
    :param if_exists: replace or append
    :param keep_only_geometry: keep only geometry
    """
    # Prepare for save it
    gdf['geometry'] = gdf['geometry'].apply(lambda x: x.wkt)
    if keep_only_geometry:
        gdf = gdf[['geometry']]
    else:
        None
    engine = create_engine(f'sqlite:///{database_name}')
    gdf.to_sql(table_name, con=engine, if_exists=if_exists, index=False)

def open_layer_from_db(database_name, table_name, crs ="EPSG:4326"):
    """
    Open a geodataframe from a sqlite database.
    :param database_name: name of the database
    :param table_name: name of the table
    :param crs: coordinate reference system
    :return: geodataframe
    """
    conn = sqlite3.connect(database_name)
    sql = f"SELECT * FROM {table_name}"
    df = pd.read_sql(sql, conn)
    df['geometry'] = df['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.crs = crs
    return gdf

def h3_index_visualizer(h3_index):
    """
    Visualize a h3 index.
    :param h3_index: h3 index
    """
    h3_boundary = h3.h3_to_geo_boundary(h3_index, geo_json=True)
    map = folium.Map(location=[h3_boundary[0][0], h3_boundary[0][1]], zoom_start=12)
    folium.Polygon(locations=h3_boundary, color='blue', fill=True).add_to(map)
    return map

def get_h3_index_from_point(point, resolution=H3_INDEX_RESOLUTION):
    """
    Get h3 index from a point.
    :param point: point
    :param resolution: resolution of the h3 index
    :return: h3 index
    """
    # <class 'shapely.geometry.point.Point'>
    if type(point) == Point:
        return h3.geo_to_h3(point.x, point.y, resolution)
    else:
        return h3.geo_to_h3(point[1], point[0], resolution)
    
def filter_geopandas_by_u_v_index(u_value, v_value, gdf):
    """
    Filter linestrings by u and v values.
    :param u_value: u value
    :param v_value: v value
    :param gdf: geodataframe
    :return: filtered geodataframe
    """
    print(u_value, v_value)
    # Filter the GeoDataFrame for rows where 'u' is u_value or 'v' is v_value
    filtered_gdf = gdf.loc[(u_value, v_value)]
    return filtered_gdf

def closest_coordinate_on_linestring(point, linestring):
    """
    Get the closest coordinate on a linestring.
    :param point: point
    :param linestring: linestring
    :return: closest coordinate
    """
    closest_point = None
    min_distance = float('inf')

    # Iterate through each coordinate in the LineString
    for coord in linestring.coords:
        ls_point = Point(coord)
        distance = point.distance(ls_point)
        if distance < min_distance:
            min_distance = distance
            closest_point = ls_point

    return closest_point

def get_routes_from_coordinates(coordinates):
    """
    Get routes from coordinates.
    :param coordinates: coordinates in WGS84 format
    :param profile: profile
    :return: routes
    """
    # Get routes
    routes = client.directions(coordinates=coordinates,
                           profile='cycling-regular',
                           format='geojson')
    return routes


def routes_to_gdf(routes):
    """
    Convert routes to a geodataframe.
    :param routes: routes
    :return: geodataframe
    """
    # Convert to geodataframe
    gdf = gpd.GeoDataFrame.from_features(routes['features'])
    gdf.crs = 'EPSG:4326'
    return gdf

def get_only_areas_which_are_crossed_by_bikelane(gdf_to_keep, bikelanes):
    if gdf_to_keep.crs != bikelanes.crs:
        raise Exception("CRS mismatch. Please make sure both geodataframes have the same CRS.")
    all_geometry_objects = objects_in_geodataframe(gdf_to_keep)
    # drop indexies 
    gdf_to_keep = gdf_to_keep.reset_index(drop=True)
    bikelanes = bikelanes.reset_index(drop=True)
    # keep only geometry columns
    gdf_to_keep = gdf_to_keep[["geometry"]]
    bikelanes = bikelanes[["geometry"]]
    if "Point" in all_geometry_objects or "LineString" in all_geometry_objects:
        gdf_to_keep = keep_only_geo_objects(gdf_to_keep)
    if "MultiPolygon" in all_geometry_objects:
        gdf_to_keep = gdf_to_keep.explode()

    if gdf_to_keep.sindex is None or bikelanes.sindex is None:
        raise Exception("Spatial index missing. Please create a spatial index for both geodataframes.")

    joined_df = gpd.sjoin(
        gdf_to_keep,
        bikelanes,
        how="left", # options are left, right, inner or outer
        predicate="intersects", # can be contains, crosses, overlaps, within, etc.
    )
    joined_df.dropna(subset=['index_right'], inplace=True)
    joined_df.drop(columns=['index_right'], inplace=True)
    joined_df = drop_duplicated_rows(joined_df)
    joined_df = joined_df[["geometry"]]

    return joined_df


# ---------------------------------------------------------------- #
#                           PREPARATION                            #
# -----------------------------------------------------------------#

def split_file(file_path, chunk_size_mb=50, output_dir="dataset/splits"):
    """
    Splits a file into multiple parts each of size `chunk_size_mb` megabytes.
    :param file_path: path to the file to split
    :param chunk_size_mb: size of each chunk in megabytes
    :param output_dir: directory to save the output files
    # Example usage
        split_file("path/to/your/large_file.osm.pbf")
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Calculate chunk size in bytes
    chunk_size_bytes = chunk_size_mb * 1024 * 1024

    # Split command for Unix-like systems
    split_cmd = ['split', '-b', str(chunk_size_bytes), file_path, os.path.join(output_dir, "part_")]

    # Execute the split command
    try:
        subprocess.run(split_cmd, check=True)
        print(f"File split into {chunk_size_mb}MB chunks in '{output_dir}' directory.")
    except subprocess.CalledProcessError as e:
        print(f"Error splitting file: {e}")


def merge_files(input_dir, output_file):
    """
    Merges multiple files from `input_dir` into a single `output_file`.
    :param input_dir: directory containing the files to merge
    :param output_file: path to the output file
    """
    # List all parts in the directory
    parts = sorted(os.listdir(input_dir))

    # Merge command for Unix-like systems
    merge_cmd = ['cat'] + [os.path.join(input_dir, part) for part in parts] + ['>', output_file]

    # Execute the merge command
    try:
        # Using shell=True to handle redirection
        subprocess.run(' '.join(merge_cmd), shell=True, check=True)
        print(f"Files merged into '{output_file}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error merging files: {e}")

def geoseries_to_geopandas(geoseries, crs, columns_to_keep = []):
    """
    Create a GeoDataFrame from a GeoSeries.
    :return: GeoDataFrame
    """
    gdf = gpd.GeoDataFrame(geoseries, columns=['geometry'])
    gdf.crs = crs
    if columns_to_keep != []:
        gdf = gdf[columns_to_keep]
    return gdf


def buffer_and_union_and_simplify_geopandas(gdf, buffer=50, simplify_value=0, debug=True):
    """
    Buffer and union a geodataframe.
    :param gdf: geodataframe
    :param buffer: buffer in meter
    :return: geodataframe
    """
    if gdf.crs != DENMARK_CRS:
        raise ValueError(f"The geodataframe must be in the correct coordinate system. In this case it must be in {DENMARK_CRS}. Now it is in {gdf.crs}.")
    else:
        if debug:
            print("buffer objects start")
        gdf = gdf.buffer(buffer)
        if debug:
            print("unary union starts")
        gdf = gdf.unary_union
        if debug:
            print("unary union ends")
        gdf = gpd.GeoSeries(gdf)
        
        gdf = geoseries_to_geopandas(gdf, DENMARK_CRS)
        if simplify_value != 0:
            if debug:
                print("simplify objects start")
            gdf = gdf.simplify(simplify_value)
            gdf = geoseries_to_geopandas(gdf, DENMARK_CRS)
        return gdf
    
def buffer_gdf(gdf, buffer=100):
    """
    Buffer a geodataframe.
    :param gdf: geodataframe
    :param buffer: buffer in meter
    :return: geodataframe
    """
    gdf = gdf.buffer(buffer)
    # convert it into a geodataframe
    gdf = geoseries_to_geopandas(gdf, gdf.crs)
    return gdf
    
def denmark_projection(gdf):
    """
    Project a geodataframe to the correct coordinate system.
    :param gdf: geodataframe
    :return: geodataframe
    """
    if gdf.crs != DENMARK_CRS:
        gdf = gdf.to_crs(DENMARK_CRS)
    return gdf


def get_already_touched_areas_along_the_way(areas_with_bikelanes, route_gdf):
    if areas_with_bikelanes.crs != route_gdf:
        raise ValueError(f"The geodataframe must be in the correct coordinate system. In this case it must be in {DENMARK_CRS}. Now it is in {areas_with_bikelanes.crs} and {route_gdf.crs}.")
    else:
        areas_already_touced = gpd.overlay(areas_with_bikelanes, route_gdf, how='intersection')
        return areas_already_touced

def get_buffered_zone(gdf, buffer=100):
    """
    Get buffered zone.
    :param gdf: geodataframe
    :param buffer: buffer in meter
    :return: geodataframe
    """
    if gdf.crs != DENMARK_CRS:
        raise ValueError(f"The geodataframe must be in the correct coordinate system. In this case it must be in {DENMARK_CRS}. Now it is in {gdf.crs}.")
    else:
        gdf = buffer_and_union_and_simplify_geopandas(gdf, buffer)
        return gdf
    
def drop_duplicated_rows(gdf):
    """
    Drop duplicated rows.
    :param gdf: geodataframe
    :return: geodataframe
    """
    gdf = gdf.drop_duplicates()
    return gdf

def keep_only_geo_objects(gdf, geometries = ["Polygon", "MultiPolygon"]):
    """
    Keep only geo objects.
    :param gdf: geodataframe
    :param geometries: geometries to keep
    :return: geodataframe
    """
    gdf = gdf[gdf.geometry.type.isin(geometries)]
    return gdf

def objects_in_geodataframe(gdf):
    return set(gdf.geometry.type)

def list_of_points_to_coordinates(list_of_points):
    coordinates = []
    # Iterate over each Point object in the list
    for point in list_of_points:
        # Extract the x and y coordinates of the Point
        x, y = point.x, point.y
        # Append the coordinates as a list to the main list
        coordinates.append([x, y])

    return coordinates




# ---------------------------------------------------------------- #
#                           Testing                                #
# -----------------------------------------------------------------#

def get_random_elements(gdf, sample=1000):
    """
    Get random elements from a geodataframe.
    :param gdf: geodataframe
    :return: geodataframe
    """
    return gdf.sample(n=sample)

def print_gdf_details(gdf):
    """
    Prints out details of a GeoDataFrame: its info, number of duplicated rows, and total memory usage.
    """
    # Printing the basic info
    print("GeoDataFrame details:")
    print(gdf.info())

    # Finding the number of duplicated rows
    num_duplicates = gdf.duplicated().sum()
    print(f"Number of duplicated rows: {num_duplicates}")

    # Finding the memory usage
    mem_usage = gdf.memory_usage(deep=True).sum()
    print(f"Memory usage (bytes): {mem_usage}")
    print(f"Memory usage (MB): {mem_usage / 1024 ** 2:.2f} MB")
    print(f"Set of geometry objects: {set(gdf.geom_type)}")


# ---------------------------------------------------------------- #
#                               UNUSED AND DECRAPTED FUNCTIONS     #
#------------------------------------------------------------------#

def add_h3_index_for_gdf(gdf, resolution=H3_INDEX_RESOLUTION):

    """
    Add h3 index for a geodataframe.
    :param gdf: geodataframe
    :return: geodataframe
    --- Highly reccomende: https://wolf-h3-viewer.glitch.me/
    """
    if gdf.crs != CRS:
        raise ValueError(f"The geodataframe must be in the correct coordinate system. In this case, it must be in {CRS}. Now it is in {gdf.crs}.")
        """    if "h3_index" in gdf.columns:
        gdf.drop(columns=['h3_index'], inplace=True)
        print(f"The geodataframe already has a column named 'h3_index'. The column has been removed. Please try again.")
        continue"""
    else:
        h3_indices = []
        for row in gdf.itertuples(index=False):
            h3_index = h3.geo_to_h3(row.geometry.centroid.y, row.geometry.centroid.x, resolution)
            h3_indices.append(h3_index)
        gdf['h3_index'] = h3_indices
        return gdf
    
def get_centorid_of_polygin(polygon):
    """
    Return lan ang long values
    """
    return polygon.centroid.x, polygon.centroid.y
