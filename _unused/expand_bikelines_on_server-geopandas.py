# ----------------------------------------------------------- #
#                            GEOPANDAS IMPLEMENTATION         #
# ----------------------------------------------------------- #

import streamlit_functions_server as sfs
import logging
#import importlib as imp
import geopandas as gpd
#import matplotlib.pyplot as plt
import functions as f
import psutil
import time

# Setup logging configuration
logging.basicConfig(filename='system_usage.log', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# Function to log system statistics
def log_system_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    logging.info(f"CPU Usage: {cpu_percent}%")
    logging.info(f"Memory Usage: {memory.percent}% used of {memory.total / (1024 ** 3):.2f}GB")

# Read data
bikelane = gpd.read_parquet('dataset/raw_unprocessed/bikelane_dk_crs_25832.parquet')
bikelane_demo = bikelane.sample(20000)
DENMARK = gpd.read_parquet('dataset/processed/borders_of_denmark_DK.parquet')

time_intervals = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]  # minutes
SPEED = 80.333
DF = bikelane_demo

for t in time_intervals:
    logging.info('#####################################################')
    logging.info(f'Starting processing for {t} minutes')
    print(f'Starting processing for {t} minutes')
    
    log_system_usage()
    
    start_time = time.time()
    bikelane_temp = DF.buffer(t * SPEED)
    logging.info('Buffer done')
    print('Buffer done')
    
    log_system_usage()
    
    temp = f.geoseries_to_geopandas(bikelane_temp, crs=f.DENMARK_CRS)
    temp_uu = f.multipolygon_to_gdf(temp.unary_union, crs=f.DENMARK_CRS)
    logging.info('Union done')
    print('Union done')
    
    log_system_usage()
    
    done = DENMARK.intersection(temp_uu)
    logging.info('Intersection done')
    done = f.geoseries_to_geopandas(done, crs=f.DENMARK_CRS)
    done.to_parquet(f'dataset/processed/bikelane_{t}_minutes_dk.parquet')
    
    log_system_usage()
    
    elapsed_time = time.time() - start_time
    logging.info(f'Saved. Elapsed time for {t} minutes: {elapsed_time:.2f} seconds')