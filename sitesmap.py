# -*- coding: utf-8 -*-
"""
Created on Wed May  1 10:52:07 2019
Simple script to plot a map of the sites.
Sites coordinates are stored in ./data/Instrument_Locs.csv
Basemap https://data.linz.govt.nz/layer/51278-chart-nz-533-firth-of-thames/
@author: Jordi
"""

import csv
import imageio
import matplotlib.pyplot as plt
import pyproj
from mpl_toolkits import basemap

# https://data.linz.govt.nz/layer/51278-chart-nz-533-firth-of-thames/
img = imageio.imread('./data/lds-chart-nz-533-firth-of-thames-JPEG/chart-nz-533-firth-of-thames.jpg')
# Sites coordinates in NZTM, need lon-lat
prj = pyproj.Proj("+proj=tmerc +lat_0=0.0 +lon_0=173.0 +k=0.9996 +x_0=1600000.0 +y_0=10000000.0 +datum=WGS84 +units=m")
m = basemap.Basemap(llcrnrlon=175.371866, llcrnrlat=-37.242242,
              urcrnrlon=175.471866, urcrnrlat=-37.134739,
              resolution='f', epsg='4326')
# m.arcgisimage(service='World_Topo_Map', verbose= True, xpixels=800, dpi=200)
plt.imshow(img, zorder=0, extent=[175.100085514,175.610142503,-37.2481637649,-36.6874800485])
with open('./data/Instrument_Locs.csv', 'r') as f:
    reader = csv.DictReader(f)
    header = reader.fieldnames
    for row in reader:
        lon, lat = prj(float(row['Easting']), float(row['Northing']), inverse=True)
        print("Site %s coordinates lon-lat: %f, %f" % (row['SiteNum'], lon, lat))
        x, y = m(lon, lat)
        m.scatter(x, y, marker = 'o', color='r', zorder=5, edgecolors= 'black')
        plt.text(x + .0025, y - .0013, "Site %s" % row['SiteNum'], fontsize=9, color='black')
plt.savefig("./output/map.png", dpi=200)
plt.show()
