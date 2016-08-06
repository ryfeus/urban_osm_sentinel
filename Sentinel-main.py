import rasterio
import numpy
import time
from skimage.util import img_as_ubyte

strFolder = '/Users/rustemfeyzkhanov/landsat/Sentinel/40RCN201607280/'
strName = '40RCN201607280'


print(strFolder+'B04.jp2')
# read red band into uint8
srcred = rasterio.open(strFolder+'B04.jp2')
r=srcred.read(1)
floatr=numpy.float64(r)
finalr=(floatr/4096)*255
finalr[finalr>255]=255
# print numpy.max(floatr)
uint8red=numpy.uint8(finalr)

print(strFolder+'B03.jp2')
# read green band into uint8
srcgreen = rasterio.open(strFolder+'B03.jp2')
g=srcgreen.read(1)
floatg=numpy.float64(g)
finalg=(floatg/4096)*255
finalg[finalg>255]=255
# print numpy.max(finalg)
uint8green=numpy.uint8(finalg)

print(strFolder+'B02.jp2')
# read blue band into uint8
srcblue = rasterio.open(strFolder+'B02.jp2')
b=srcblue.read(1)
floatb=numpy.float64(b)
finalb=(floatb/4096)*255
finalb[finalb>255]=255
# print numpy.max(finalb)
uint8blue=numpy.uint8(finalb)

print(strName+'_RGB.tif')
# setup output product
profile = srcred.meta
profile.update(nodata=0,dtype='uint8',driver='GTiff',count=3,compress='lzw')
outputpath=strName+'_RGB.tif'
output = rasterio.open(outputpath, 'w', **profile)

print('Write '+strName+'_RGB.tif')
#fill output channels with bands
output.write_band(1, img_as_ubyte(uint8red))
output.write_band(2, img_as_ubyte(uint8green))
output.write_band(3, img_as_ubyte(uint8blue))

print time.clock()-tic