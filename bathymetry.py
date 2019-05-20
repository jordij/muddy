import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

data_path = './data/transect_bathymetry.csv'
df = pd.read_csv(data_path)
df = df.apply(pd.to_numeric, errors='coerce')
# sites distance in m
sites = [
    0.0,
    486.9258201722962,
    1507.2329501732236,
    2597.228501656257,
    6239.191158574506
]
dfsites = df.loc[df['x'].isin(sites)]
sns.set(rc={'figure.figsize': (11, 4)})
fig, ax = plt.subplots(nrows=1, ncols=1)
plt.yticks(np.arange(-3, 4, 1))
ax.plot((df.x/1000), df.y)
plt.stem(dfsites.x/1000, dfsites.y, bottom=-3, linefmt='C0--', basefmt=' ')
plt.xlabel("Distance (km)")
plt.ylabel("Elevation (m +MSL)")
ax.axis([-0.5, 7, -3, 3])
ax.set_xticks([s/1000 for s in sites], minor=True)
# Sites labels
y = 0
for i, r in dfsites.iterrows():
    plt.annotate("S%i" % y, xy=(r["x"]/1000,
                 r["y"]), xytext=(r["x"]/1000 + 0.1, r["y"]), size="15")
    y += 1
fig.tight_layout()
plt.savefig("./output/bathymetry.png", bbox_inches='tight', dpi=200)
plt.show()
plt.close()
