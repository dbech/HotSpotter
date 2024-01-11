import os
import math
import numpy
import xmltodict
import simplekml
from thermal import Thermal
from PIL import Image
from geographiclib.geodesic import Geodesic
from datetime import datetime

TEMPERATURE_MASK = 100 # we're looking for tempuratures in cencius greater than this value.
CAMERA_FOCAL_LENGTH = 38 # millimeter full frame equiv https://enterprise.dji.com/mavic-2-enterprise-advanced/specs 
CAMERA_SENSOR_HEIGHT = 24 # millimeter full frame equiv
CAMERA_SENSOR_WIDTH = 36 # millimeter full frame equiv

def calculate_gsd(camera_altitude, camera_sensor_mm, camera_focal_length, image_px):
    return ((camera_altitude*1000) * camera_sensor_mm) / (camera_focal_length * image_px)

directory = os.fsencode('input/')
geod = Geodesic(6378137.0, 0.003352810681183637418) # https://www.legislation.gov.au/F2017L01352/latest/text https://en.wikipedia.org/wiki/Geodetic_Reference_System_1980
kml = simplekml.Kml(name=datetime.today().strftime('%Y-%m-%d'))
hotspot_style = simplekml.Style(iconstyle=simplekml.IconStyle(scale=0.8, icon=simplekml.Icon(href='http://maps.google.com/mapfiles/kml/shapes/firedept.png')), labelstyle=simplekml.LabelStyle(scale=0.4))
    
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".JPG"):
        image_path = f'input/{filename}' # @todo: change to recusively work through a folder
        image = Image.open(image_path)
        image_height = image.height
        image_width = image.width
        image.close()

        file = open(image_path, encoding = 'latin-1')
        file_bytes = file.read()
        file.close()
        xmp_str = file_bytes[file_bytes.find('<x:xmpmeta'):file_bytes.find('</x:xmpmeta')+12] # look for everything enclosed in the root of our XMP data
        xmp_dict = xmltodict.parse(xmp_str).get('x:xmpmeta').get('rdf:RDF').get('rdf:Description') # convert our XML-like string of XMP data and strip of some of the fluff
        assert isinstance(xmp_dict, dict)

        camera_altitude = float(xmp_dict.get('@drone-dji:RelativeAltitude').replace('+', '')) # since we need to know the size of the object in the image and the object in the image is the ground we'll need the distance to the ground to calculate it's size
        camera_heading = float(xmp_dict.get('@drone-dji:GimbalYawDegree').replace('+', '')) # we need this to orient the image relative to north

        GSDh = calculate_gsd(camera_altitude, CAMERA_SENSOR_HEIGHT, CAMERA_FOCAL_LENGTH, image_height) # how tall is a pixel mm
        GSDw = calculate_gsd(camera_altitude, CAMERA_SENSOR_WIDTH, CAMERA_FOCAL_LENGTH, image_width) # how wide is a pixel mm

        thermal = Thermal( # instance a Thermal object and pass it the SDK
            dirp_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libdirp.dll',
            dirp_sub_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libv_dirp.dll',
            iirp_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libv_iirp.dll',
            exif_filename='plugins/exiftool-12.35.exe',
            dtype=numpy.float32,
        )
        temperature = thermal.parse_dirp2(image_filename=image_path, image_height=image_height, image_width=image_width, m2ea_mode=True) # m2ea refers to the mavic 2 enterprice advance drone
        assert isinstance(temperature, numpy.ndarray) # check we got the 2D array we're expecting
        mask_result_indexes = numpy.where(temperature > TEMPERATURE_MASK)
        try:
            assert len(mask_result_indexes[0]) > 0
        except:
            print(f'No hotspots found in {image_path}')
            continue

        for i in enumerate(mask_result_indexes[0]):
            centre = numpy.array([image_width/2, image_height/2])
            north = numpy.array([image_width/2, 0])
            hotspot = numpy.array([mask_result_indexes[1][i[0]], i[1]])

            north_vector = centre - north
            hotspot_vector = centre - hotspot
            angle = (numpy.degrees(math.atan2(numpy.linalg.det([north_vector, hotspot_vector]), numpy.dot(north_vector, hotspot_vector))) + camera_heading) % 360
            distance = numpy.linalg.norm(hotspot_vector) * (((GSDh+GSDw)/2)/1000) # this is probably inaccurate, should do the math ourselves to apply GSD per axis

            direct_dict = geod.Direct(float(xmp_dict['@drone-dji:GpsLatitude'].replace('+', '')), float(xmp_dict['@drone-dji:GpsLongitude'].replace('+', '')), angle, distance)
            kml.newpoint(name=f'{temperature[i[1]][mask_result_indexes[1][i[0]]]:.2f}\N{DEGREE SIGN}C', description=f'File Name: {image_path.replace('input/', '')}\nCapture Date: {xmp_dict['@xmp:CreateDate']}\nCaptured By: {xmp_dict['@tiff:Model']}', coords=[(direct_dict['lon2'], direct_dict['lat2'])], altitudemode=simplekml.AltitudeMode.clamptoground).style=hotspot_style

kml.save(f'output/{datetime.today().strftime('%Y-%m-%d')}.kml')