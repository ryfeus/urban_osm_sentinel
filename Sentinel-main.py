import rasterio
import numpy
import time
import utm
import json
from skimage.util import img_as_ubyte
from scipy import ndimage

strFolder = '/Applications/MAMP/htdocs/urban_osm_sentinel/40RCN201607280/'
strName = 'Dubai'

tic = time.clock()



def pointToIndexSentinel(point,src):
    points = utm.from_latlon(point[0], point[1],force_zone_number=int(src.meta['crs']['init'][8:10]))[0:2]
    # points = latlngToMerc(point[0],point[1])
    # print points
    ((indx,c),(indy,b)) = src.window(*(points+points))
    return (indx,indy)

def point_in_poly(x,y,poly):
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside


print(strFolder+'B04.tif')
# read red band into uint8
vecBands = ['B01','B02','B03','B04','B05','B06','B07','B08','B09','B10','B11','B12']

# 1 - 4
# 2 - 1
# 3 - 1
# 4 - 1
# 5 - 2
# 6 - 2
# 7 - 2
# 8 - 1
# 9 - 3
# 10 - 3
# 11 - 2
# 12 - 2


with open('data.geojson') as data_file:    
    dataRaw = json.load(data_file)

vecPolygonsData=[]
vecBandData = {}

for i in range(len(dataRaw['features'])):
       vecPolygonsData.append({})

for band in vecBands:
	src = rasterio.open(strFolder+band+'.tif')
	arrBand=src.read(1)
	arrBandFloat=numpy.float64(arrBand)
	arrBandFinal=(arrBandFloat/4096)*255
	arrBandFinal[arrBandFinal>255]=255
	arrBanduint8=numpy.uint8(arrBandFinal)


	vecPolygons = []
	for i in range(len(dataRaw['features'])):
		polygon = []
		for j in range(len(dataRaw['features'][i]['geometry']['coordinates'][0])):
			pointLatLng = dataRaw['features'][i]['geometry']['coordinates'][0][j]
			pointInd = pointToIndexSentinel((pointLatLng[1],pointLatLng[0]),src)
			polygon.append([pointInd[0],pointInd[1]])
		vecPolygons.append(polygon)

	vecPolygonsNum = []
	vecPolygonsNumAll = []
	vecPolygonsMean = []
	vecPolygonsStd = []
	vecPolygonsLen = []
	for k in range(len(vecPolygons)):
		polygonInd = vecPolygons[k]
		numMinX = int(min(polygonInd, key = lambda t: t[0])[0])
		numMaxX = int(max(polygonInd, key = lambda t: t[0])[0])
		numMinY = int(min(polygonInd, key = lambda t: t[1])[1])
		numMaxY = int(max(polygonInd, key = lambda t: t[1])[1])

		polygonsNum = []
		polygonsLat = []
		polygonsLng = []
		for i in range(numMinX-1,numMaxX+1):
		    for j in range(numMinY-1,numMaxY+1):
		        if point_in_poly(i,j,polygonInd):
		        	polygonsNum.append(arrBanduint8[i,j])
		        	polygonsLat.append(i)
		        	polygonsLng.append(j)
		vecPolygonsNum.append(polygonsNum)
		vecPolygonsLen.append(len(polygonsNum))
		vecPolygonsMean.append(numpy.mean(polygonsNum))
		vecPolygonsStd.append(numpy.std(polygonsNum))
		vecPolygonsNumAll = numpy.concatenate((vecPolygonsNumAll,polygonsNum),axis=0)

		vecPolygonsData[k][band] = {}
		vecPolygonsData[k][band]['vecPolygonsNum'] = vecPolygonsNum
		vecPolygonsData[k][band]['vecPolygonsLen'] = vecPolygonsLen
		vecPolygonsData[k][band]['vecPolygonsMean'] = vecPolygonsMean
		vecPolygonsData[k][band]['vecPolygonsStd'] = vecPolygonsStd
		vecPolygonsData[k][band]['polygonsLat'] = polygonsLat
		vecPolygonsData[k][band]['polygonsLng'] = polygonsLng
	# print(numpy.mean(vecPolygonsNumAll))
	# print(band+' mean:'+str(numpy.mean(vecPolygonsNumAll))+" std:"+str(numpy.std(vecPolygonsNumAll)))
	vecBandData[band] = {}
	vecBandData[band]['mean'] = numpy.median(vecPolygonsNumAll)
	vecBandData[band]['std'] = numpy.std(vecPolygonsNumAll)

# print(vecPolygonsData)

print(strFolder+'B04.tif')
# read red band into uint8
srcred = rasterio.open(strFolder+'B04.tif')
r=srcred.read(1)
floatr=numpy.float64(r)
finalr=(floatr/4096)*255
finalr[finalr>255]=255
uint8red=numpy.uint8(finalr)

print(strFolder+'B03.tif')
# read green band into uint8
srcgreen = rasterio.open(strFolder+'B03.tif')
g=srcgreen.read(1)
floatg=numpy.float64(g)
finalg=(floatg/4096)*255
finalg[finalg>255]=255
# print numpy.max(finalg)
uint8green=numpy.uint8(finalg)

print(strFolder+'B02.tif')
# read blue band into uint8
srcblue = rasterio.open(strFolder+'B02.tif')
b=srcblue.read(1)
floatb=numpy.float64(b)
finalb=(floatb/4096)*255
finalb[finalb>255]=255
# print numpy.max(finalb)
uint8blue=numpy.uint8(finalb)

# bandScenes = numpy.zeros(((uint8red.shape[0], uint8red.shape[1]), dtype=bool))
bandScenes = numpy.zeros((uint8red.shape[0], uint8red.shape[1]), dtype=bool)
for i in range(uint8red.shape[0]):
	for j in range(uint8red.shape[1]):
		flagRed = (uint8red[i,j] > (vecBandData['B04']['mean']-vecBandData['B04']['std']/3))&((uint8red[i,j] < (vecBandData['B04']['mean']+vecBandData['B04']['std']/3)))
		flagGreen = (uint8green[i,j] > (vecBandData['B03']['mean']-vecBandData['B03']['std']/3))&((uint8green[i,j] < (vecBandData['B03']['mean']+vecBandData['B03']['std']/3)))
		flagBlue = (uint8blue[i,j] > (vecBandData['B02']['mean']-vecBandData['B02']['std']/3))&((uint8blue[i,j] < (vecBandData['B02']['mean']+vecBandData['B02']['std']/3)))
		if (flagRed&flagGreen&flagBlue):
			bandScenes[i,j] = True
			# uint8red[i,j] = 1
			# uint8green[i,j] = 255
			# uint8blue[i,j] = 1

arrElement = [[0, 1, 0],[1, 1, 1],[0, 1, 0]]
# arrElement = [  [0, 0, 1, 0, 0],
#                 [0, 1, 1, 1, 0],
#                 [1, 1, 1, 1, 1],
#                 [0, 1, 1, 1, 0],
#                 [0, 0, 1, 0, 0]]

bandScenes = ndimage.binary_opening(bandScenes.astype(int),structure=arrElement)
uint8red[bandScenes] = 1
uint8green[bandScenes] = 255
uint8blue[bandScenes] = 1

for k in range(len(vecPolygonsData)):
	for i in range(len(vecPolygonsData[k]['B02']['polygonsLat'])):
		uint8red[vecPolygonsData[k]['B02']['polygonsLat'][i],vecPolygonsData[k]['B02']['polygonsLng'][i]] = 1
		uint8green[vecPolygonsData[k]['B02']['polygonsLat'][i],vecPolygonsData[k]['B02']['polygonsLng'][i]] = 1
		uint8blue[vecPolygonsData[k]['B02']['polygonsLat'][i],vecPolygonsData[k]['B02']['polygonsLng'][i]] = 255

print(strName+'_RGB.tif')
# setup output product
profile = srcred.meta
profile.update(nodata=0,dtype='uint8',driver='GTiff',count=3,compress='lzw')
outputpath=strName+'_RGB.tif'
output = rasterio.open(outputpath, 'w', **profile)

print('Write '+strName+'_RGB.tif')
#fill output channels with bands
output.write_band(1, img_as_ubyte(bandScenes.astype(int)))
output.write_band(2, img_as_ubyte(bandScenes.astype(int)*255))
output.write_band(3, img_as_ubyte(bandScenes.astype(int)))
# output.write_band(1, img_as_ubyte(uint8red))
# output.write_band(2, img_as_ubyte(uint8green))
# output.write_band(3, img_as_ubyte(uint8blue))

print time.clock()-tic