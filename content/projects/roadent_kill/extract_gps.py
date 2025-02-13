import toml

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pillow_heif import register_heif_opener
from glob import glob

register_heif_opener()

# this is a much more succinct version where the labels are surfaced using the GPSTAGS
def get_geo(exif):
    for key, value in TAGS.items():
        if value == "GPSInfo":
            break
    gps_info = exif.get_ifd(key)
    return {
        GPSTAGS.get(key, key): value
        for key, value in gps_info.items()
    }

def get_gps_in_degrees(gps):
    lat = gps['GPSLatitude']
    lat_ref = gps['GPSLatitudeRef']
    lat = float(lat[0]+(lat[1]/60)+(lat[2]/(3600*100)))
    lat = -lat if lat_ref == 'S' else lat

    long = gps['GPSLongitude']
    long_ref = gps['GPSLongitudeRef']
    long = float(long[0]+(long[1]/60)+(long[2]/(3600*100)))
    long = -long if long_ref == 'W' else long

    
    return (lat,long)

imgs_paths = glob('*.HEIC')
gps_coords = list()
for img_path in imgs_paths:
    img = Image.open(img_path)

    exif = img.getexif()
    # ifd = exif.get_ifd(0x8825)

    gps = get_geo(exif)
    gps_coords.append(gps)
    
coord_map = {img_path: coord for img_path, coord 
             in zip(imgs_paths, gps_coords)}
# TODO: toml writes floats and array of floats to disk as str
# this is annoying because I need to account for that when reading
# from disk. troubleshooted for a while and couldn't figure it out 
toml.dump(coord_map, open('roadent_kill_gps_coords.toml', 'w'));
