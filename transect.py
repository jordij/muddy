# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from mpl_toolkits import basemap

# transect map
lons = [175.416278, 175.445361, 175.445361, 175.4162781]
lats = [-37.206863, -37.206863, -37.155814, -37.155814]

fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.9, 0.9])
m = basemap.Basemap(llcrnrlon=174.646912, llcrnrlat=-37.324305,
                    urcrnrlon=175.819702, urcrnrlat=-36.604504,
                    resolution='f', projection="tmerc", lat_0=-37, lon_0=175)
m.drawcoastlines()
m.fillcontinents()
m.drawparallels(np.arange(-90, 90, 0.25), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180, 180, 0.5), labels=[1, 0, 0, 1])
circle = Circle(m((lons[0] + lons[1])/2, (lats[1] + lats[2])/2),
                color='r', radius=(m.ymax - m.ymin) / 15, fill=True, alpha=0.8)
plt.gca().add_patch(circle)
plt.savefig("./output/transect.png", dpi=300, bbox_inches='tight')
plt.show()
plt.close()
