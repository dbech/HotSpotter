import numpy
import xmltodict
from thermal import Thermal
from PIL import Image

TEMPERATURE_MASK = 145 # we're looking for tempuratures in cencius greater than this value.
CAMERA_FOCAL_LENGTH = 38 # millimeter full frame equiv https://enterprise.dji.com/mavic-2-enterprise-advanced/specs 
CAMERA_SENSOR_HEIGHT = 24 # millimeter full frame equiv
CAMERA_SENSOR_WIDTH = 36 # millimeter full frame equiv

def calculate_gsd(camera_altitude, camera_sensor_mm, camera_focal_length, image_px):
    return ((camera_altitude*1000) * camera_sensor_mm) / (camera_focal_length * image_px)

image_path = 'input/DJI_0007_T.JPG' # @todo: change to recusively work through a folder
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
camera_heading = xmp_dict.get('@drone-dji:GimbalYawDegree') # we need this to orient the image relative to north

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

print(GSDh*image_height/1000)
print(GSDw*image_width/1000)