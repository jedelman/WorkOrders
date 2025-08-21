import geopandas as gpd
import db
import shapely
import json
import re

quotefix = re.compile("'")

addrs = gpd.GeoDataFrame(db.get_addresses_from_local_db())
addrs = addrs.dropna(subset=['geocoded_column'])

def convertgeo(item):
    try:
        return shapely.geometry.shape(
            json.loads(
                quotefix.sub('"', item)))
    except Exception as x:
        print({"ERROR":"ERROR", "item":item, "x":x})


addrs['geometry'] = addrs['geocoded_column'].apply(convertgeo)
