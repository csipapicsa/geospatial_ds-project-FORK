from memory_profiler import profile
import geopandas as gpd
import functions as f
import logging
import time

# Setup logging for memory usage
logging.basicConfig(filename='memory_usage.log', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# Decorate functions with @profile to monitor their memory usage
@profile
def process_bikelanes(t, DF, DENMARK, SPEED):
    print("#######################################")
    print(f'Starting processing for {t} minutes')
    #logging.info(f'Starting processing for {t} minutes')
    print('Buffer started')
    bikelane_temp = DF.buffer(t * SPEED)
    #logging.info('Buffer done')
    print('Buffer done, union started')
    
    temp = f.geoseries_to_geopandas(bikelane_temp, crs=f.DENMARK_CRS)
    temp_uu = f.multipolygon_to_gdf(temp.unary_union, crs=f.DENMARK_CRS)
    #logging.info('Union done')
    print('Union done, intersection started')
    
    done = DENMARK.intersection(temp_uu)
    #logging.info('Intersection done')
    done = f.geoseries_to_geopandas(done, crs=f.DENMARK_CRS)
    done.to_parquet(f'dataset/processed/bikelane_{t}_minutes_dk.parquet')
    #logging.info('Saved')

# Main function to run process
def main():
    bikelane = gpd.read_parquet('dataset/raw_unprocessed/bikelane_dk_crs_25832.parquet')
    DENMARK = gpd.read_parquet('dataset/processed/borders_of_denmark_DK.parquet')
    time_intervals = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]  # minutes
    SPEED = 80.333
    DF = bikelane.sample(200)
    DF = bikelane

    for t in time_intervals:
        process_bikelanes(t, DF, DENMARK, SPEED)

if __name__ == "__main__":
    main()