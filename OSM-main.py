import rasterio
import numpy
from skimage.util import img_as_ubyte
import os
import time
import urllib2
import sys
import json
from osmread import parse_file, Way, Node, Relation

tic = time.clock()

# url = 'http://www.overpass-api.de/api/xapi_meta?*[building=yes][bbox=55.09094238281249,24.931898803604035,55.33538818359375,25.116067121686175]'
# fileOSM = urllib2.urlopen(url)
# with open('buildings.osm','wb') as output:
# 	output.write(fileOSM.read())
vecNodes = {}
geoJson = {}
geoJson['type'] = 'FeatureCollection'
geoJson['crs'] = { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } }
geoJson['features'] = []
for entity in parse_file('buildings.osm'):
	if isinstance(entity, Node):
		vecNodes[str(entity.id)] = {'lat':entity.lat,'lng':entity.lon}
	elif isinstance(entity, Way):
		vecPolygon = []
		for node in entity.nodes:
			vecPolygon.append([vecNodes[str(node)]['lng'],vecNodes[str(node)]['lat']])
		dataFeature = {}
		dataFeature['type']='Feature'
		dataFeature['properties']={}
		dataFeature['geometry']={}
		dataFeature['geometry']['type']='Polygon'
		dataFeature['geometry']['coordinates']=[vecPolygon]
		geoJson['features'].append(dataFeature)
with open('data.geojson', 'w') as outfile:
    json.dump(geoJson, outfile)

print(time.clock()-tic)