import numpy as np
import sys
from thermal import Thermal

flight_h = 154.692 #meters (need to source from image, got this from metadata)
camera_focal_length = 38 #millimeter full frame equiv https://enterprise.dji.com/mavic-2-enterprise-advanced/specs 
camera_sensor_h = 24 #millimeter full frame
camera_sensor_w = 36 #millimeter full frame
image_h = 512 #pixels https://enterprise.dji.com/mavic-2-enterprise-advanced/specs
image_w = 640 #pixels https://enterprise.dji.com/mavic-2-enterprise-advanced/specs

np.set_printoptions(threshold=sys.maxsize-1)
thermal = Thermal(
    dirp_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libdirp.dll',
    dirp_sub_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libv_dirp.dll',
    iirp_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libv_iirp.dll',
    exif_filename='plugins/exiftool-12.35.exe',
    dtype=np.float32,
)

temperature = thermal.parse_dirp2(image_filename='input/DJI_0001_T.JPG', image_height=image_h, image_width=image_w, m2ea_mode=True) # m2ea refers to the mavic 2 enterprice advance drone
assert isinstance(temperature, np.ndarray)

GSDh = ((flight_h*1000) * camera_sensor_h) / (camera_focal_length * image_h)
GSDw = ((flight_h*1000) * camera_sensor_w) / (camera_focal_length * image_w)
print((GSDh * image_h)/1000) #meters
print((GSDw * image_w)/1000) #meters

#search the array for pixels with values within some range
#implement vincenty's direct or it's inverse via library to get the coords of the pixel
#generate a KML with the location of each pixel