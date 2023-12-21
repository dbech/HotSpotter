import numpy as np
import sys
from thermal import Thermal

np.set_printoptions(threshold=sys.maxsize-1)
thermal = Thermal(
    dirp_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libdirp.dll',
    dirp_sub_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libv_dirp.dll',
    iirp_filename='plugins/dji_thermal_sdk_v1.1_20211029/windows/release_x64/libv_iirp.dll',
    exif_filename='plugins/exiftool-12.35.exe',
    dtype=np.float32,
)

temperature = thermal.parse_dirp2(image_filename='input/DJI_0001_T.JPG', m2ea_mode=True)
assert isinstance(temperature, np.ndarray)

print(temperature.max())
print(temperature.min())
print(temperature)

#alt 154.692
#focal length ~9mm
# GSDh= flight height x sensor height / focal length x image height;
# GSDw= flight height x sensor width / focal length x image width