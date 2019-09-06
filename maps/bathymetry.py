import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from constants import BATHYMETRY_PATH, SITES_DISTANCES, OUTPUT_PATH


def plot_bathymetry():
    df = pd.read_csv(BATHYMETRY_PATH)
    df = df.apply(pd.to_numeric, errors="coerce")
    dfsites = df.loc[df["x"].isin(SITES_DISTANCES)]
    sns.set_style("ticks")
    fig, ax = plt.subplots(nrows=1, ncols=1)
    plt.yticks(np.arange(-3, 4, 1))
    ax.plot((df.x/1000), df.y)
    plt.stem(dfsites.x/1000, dfsites.y, bottom=-3, linefmt="C0--", basefmt=" ")
    plt.xlabel("Distance [km]")
    plt.ylabel("Elevation [m +MSL]")
    ax.axis([-0.5, 7, -3, 3])
    ax.set_xticks([s/1000 for s in SITES_DISTANCES], minor=True)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    # Sites labels
    y = 0
    for i, r in dfsites.iterrows():
        plt.annotate("S%i" % (y + 1), xy=(r["x"]/1000,
                     r["y"]), xytext=(r["x"]/1000 + 0.1, r["y"]), size="22")
        y += 1
    fig.tight_layout()
    plt.savefig("%sbathymetry.png" % OUTPUT_PATH, bbox_inches="tight", dpi=300)
    fig.show()
    del fig
