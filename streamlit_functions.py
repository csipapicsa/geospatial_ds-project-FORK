def geodataframe_to_map_converter(gdf):
    """
    Display a geodataframe on a map.
    :param gdf: geodataframe
    :param zoom: zoom level
    :param height: height of the map
    :param width: width of the map
    """
    coordinates = gdf.geometry.centroid
    latitude = coordinates.y  # y-coordinate is latitude
    longitude = coordinates.x  # x-coordinate is longitude
    gdf['latitude'] = latitude
    gdf['longitude'] = longitude

    return gdf