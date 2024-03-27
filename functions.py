# ---------------------------------------------------------------- #
#                          IMPORTS - Obviously                     #
# -----------------------------------------------------------------#

import geopandas as gpd
import pandas as pd
from shapely import wkt

# database, sql
from sqlalchemy import create_engine
import sqlite3
import subprocess
import os

# ---------------------------------------------------------------- #
#                          GLOBAL VARIABLES                        #
# -----------------------------------------------------------------#

TEST_DATABASE = "test_database.db"
DATABASE_RAW = "denmark_raw.db"
DATABASE_CLEAN = "denmark_clean.db"
CRS = "EPSG:4326" # global
DENMARK_CRS = "EPSG:25832"

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

def geoseries_to_geopandas(geoseries, columns_to_keep = []):
    """
    Create a GeoDataFrame from a GeoSeries.
    :return: GeoDataFrame
    """
    gdf = gpd.GeoDataFrame(geoseries, columns=['geometry'])
    gdf.crs = DENMARK_CRS
    if columns_to_keep != []:
        gdf = gdf[columns_to_keep]
    return gdf