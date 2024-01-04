import numpy as np
import xmltodict
from thermal import Thermal
from PIL import Image

TEMPERATURE_MASK = 145 #we're looking for tempuratures in cencius greater than this value.

flight_h = 113 #meters (need to source from image, got this from metadata)
camera_focal_length = 38 #millimeter full frame equiv https://enterprise.dji.com/mavic-2-enterprise-advanced/specs 
camera_sensor_h = 24 #millimeter full frame
camera_sensor_w = 36 #millimeter full frame

image_path = 'input/DJI_0127_T.JPG'
image = Image.open(image_path)
image_h = image.height
image_w = image.width
image.close()

file = open(image_path, encoding = 'latin-1')
file_bytes = file.read()
file.close()
xmp_str = file_bytes[file_bytes.find('<x:xmpmeta'):file_bytes.find('</x:xmpmeta')+12]
xmp_dict = xmltodict.parse(xmp_str)

thermal = Thermal(
    dirp_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libdirp.dll',
    dirp_sub_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libv_dirp.dll',
    iirp_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libv_iirp.dll',
    exif_filename='plugins/exiftool-12.35.exe',
    dtype=np.float32,
)
temperature = thermal.parse_dirp2(image_filename=image_path, image_height=image_h, image_width=image_w, m2ea_mode=True) # m2ea refers to the mavic 2 enterprice advance drone
assert isinstance(temperature, np.ndarray)

mask_result_indexes = np.where(temperature > TEMPERATURE_MASK)

print("  X,   Y | Tempurature")
print("----------------------")
for i in enumerate(mask_result_indexes[0]):
    x = mask_result_indexes[1][i[0]]
    y = i[1]
    print(str(x) + ", " + str(y) + " | " + str(temperature[y][x]))

GSDh = ((flight_h*1000) * camera_sensor_h) / (camera_focal_length * image_h) #make a function for this
GSDw = ((flight_h*1000) * camera_sensor_w) / (camera_focal_length * image_w)