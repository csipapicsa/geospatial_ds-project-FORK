# ----------------------------------------------------------- #
#                            GEODASK IMPLEMENTATION           #
# ----------------------------------------------------------- #


import dask_geopandas as dgd
from dask.distributed import Client
import geopandas as gpd
import functions as f

client = Client(n_workers=8, threads_per_worker=1)

# ----------------------------------------------------------- #

# Load data using Dask-GeoPandas
bikelane = dgd.read_parquet('dataset/raw_unprocessed/bikelane_dk_crs_25832.parquet')
DENMARK = dgd.read_parquet('dataset/processed/borders_of_denmark_DK.parquet')

bikelane_demo = bikelane.sample(frac=0.01)  # Adjust sample size as needed


# ----------------------------------------------------------- #

# Assuming you have already read the 'bikelane' as a Dask-GeoDataFrame
def process_chunk(gdf):
    # Directly apply buffer if supported, or convert each chunk to GeoPandas, apply buffer, and convert back
    buffered = gdf.buffer(SPEED * 5)  # Apply buffer directly if this line throws an error, use GeoPandas manually in the chunk
    return buffered


# ----------------------------------------------------------- #

# Apply the function to each partition
buffered_bikelanes = bikelane.map_partitions(process_chunk, meta=bikelane._meta)


SPEED = 80.333
DF = bikelane_demo

# Optional: Convert back to a Dask DataFrame for further distributed operations or continue with geospatial operations
# Example to compute the result back into a single GeoDataFrame
result_gdf = buffered_bikelanes.compute()  # Be cautious with .compute() as it pulls all data into memory

def process_time(t):
    print(f'Minutes: {t}')
    bikelane_temp = DF.buffer(t * SPEED)
    print('Buffer done')
    temp = f.geoseries_to_geopandas(bikelane_temp.to_geopandas(), crs=f.DENMARK_CRS)
    temp_uu = f.multipolygon_to_gdf(temp.unary_union, crs=f.DENMARK_CRS)
    print('Union done')
    done = DENMARK.intersection(temp_uu)
    print('Intersection done')
    done = f.geoseries_to_geopandas(done.to_geopandas(), crs=f.DENMARK_CRS)
    done.to_parquet(f'dataset/processed/bikelane_{t}_minutes_dk.parquet')
    print('Saved')

# Processing in parallel
results = [process_time(t) for t in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]]