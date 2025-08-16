import db
import geopandas as gpd
import sys

def refresh_civic_leagues():
    print("getting civic leagues")
    civic_leagues = db.get_civic_leagues_from_local_file()
    print(f"got {len(civic_leagues)} leagues")

    print("uploading.")
    civic_leagues.to_postgis(db.DB_NAMES.CIVIC_LEAGUES, db.engine)
    print("success!")

def refresh_addresses():
    print("getting addresses")
    addresses = gpd.GeoDataFrame(db.get_addresses_from_local_db())
    print(f"got {len(addresses)} addressess")

    print("writing addresses")
    addresses.to_postgis('norfolk_addresses', db.engine)
    print(f"wrote {len(addresses)} addresses")

def refresh_postgis_mynorfolk():
    print("getting mynorfolk data")
    mnf = db.get_mnf_from_socrata()
    print(f"got {len(mnf)} rows")

    # print('getting addresses')
    # addresses = db.get_addresses()
    # print(f"got {len(addresses)} addresses")

    # addresses = addresses.set_index(['full_address'])

    # print("setting geometry")
    # print("trimming location string")
    # mnf[['address']] = mnf['location'].str.replace(', NORFOLK, VA', '')

    # def getGeometry(row):
    #     try:
    #         return addresses.loc[row['address']]['geometry']
    #     except Exception as e:
    #         return None

    # print("merging with address geometry")
    # mnf['geometry'] = mnf.apply(getGeometry, axis=1)

    # print("setting geometry")    
    # mnf.set_geometry('geometry')
    print("success! uploading...")
    mnf.to_sql('mynorfolk', db.engine)
    print("upload complete!")


command = sys.argv[1]

print(sys.argv)

print(f"Running command '{command}'")

match command:
    case "refresh-addresses":
        refresh_addresses()
    
    case "refresh-mynorfolk":
        refresh_postgis_mynorfolk()
    
    case "refresh-civic-leagues":
        refresh_civic_leagues()

    case default:
        None