import geopandas as gpd
import pandas as pd
from shapely import wkt

# database, sql
from sqlalchemy import create_engine
import sqlite3

# define gloabal variables
TEST_DATABASE = "test_database.db"
DATABASE_RAW = "denmark_raw.db"
DATABASE_CLEAN = "denmark_clean.db"
CRS = "EPSG:4326" # global
DENMARK_CRS = "EPSG:25832"


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