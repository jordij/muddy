import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from constants import (BATHYMETRY_PATH, SITES_DISTANCES,
                       OUTPUT_PATH, KARIN_PATH, ANDREW_PATH)
from tools import plotter


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


def plot_profile():
    df = pd.read_csv(KARIN_PATH, sep=r"\s+")
    df = df.apply(pd.to_numeric, errors="coerce")
    sns.set_style("ticks")
    plotter.set_font_sizes(big=True)
    fig, ax = plt.subplots()
    ax.plot(df.Distance, df.Elevation, c="black")
    ax.plot(df.loc[37].Distance, df.loc[37].Elevation, 'o', label="Site 1", c="red")  # site 1 marker
    # ax.plot(df.loc[35].Distance, df.loc[35].Elevation, 'x', label="Fringe")  # fringe marker
    ax.axvline(df.loc[34].Distance, linestyle="--", c="black")
    #, [df.loc[34].Elevation], bottom=0, markerfmt=None, linefmt="--", basefmt=" ")
    ax.text(30, 0.2, "Mangrove Forest")
    ax.text(70, 0.2, "Fringe")
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)
    ax.legend()
    ax.set_ylabel("Elevation [m +MSL]")
    ax.set_xlabel("Distance [m]")


def plot_aprofile():
    df = pd.read_csv(ANDREW_PATH, sep=r"\s+")
    df = df.apply(pd.to_numeric, errors="coerce")
    df_east = pd.read_csv("./data/AndrewProfile_east.csv", sep=r"\s+")
    df_east = df_east.apply(pd.to_numeric, errors="coerce")
    df_west = pd.read_csv("./data/AndrewProfile_west.csv", sep=r"\s+")
    df_west = df_west.apply(pd.to_numeric, errors="coerce")

    sns.set_style("ticks", {"figure.figsize": (16, 10)})
    plotter.set_font_sizes(big=True)
    fig, axes = plt.subplots(3, sharex=True)

    axes[0].plot(df.Distance, df.Elevation, '-o', c="black",
                 label="Elevation\ncenter")
    axes[1].plot(df_west.Distance, df_west.Elevation, '-o', c="green",
                 label="Elevation\nwest")
    axes[2].plot(df_east.Distance, df_east.Elevation, '-o', c="blue",
                 label="Elevation\neast")

    s1_d = (df.loc[10].Distance + df.loc[11].Distance)/2
    s1_e = (df.loc[10].Elevation + df.loc[11].Elevation)/2

    for ax in axes:
        ax.axvline(s1_d, linestyle=":", c="red", alpha=0.3)
        ax.axvline(df.loc[6].Distance, linestyle="--", c="black", alpha=0.5)
        ax.axvline(df.loc[16].Distance, linestyle="--", c="black", alpha=0.5)
        ax.set_xlim(-25, None)
        ax.set_ylim(0, None)
    for ax in axes:
        ax.legend(frameon=False, bbox_to_anchor=(-0.05, 0.75))
    axes[2].text(-15, 0.2, "Forest")
    axes[2].text(10.25, 0.2, "Fringe")
    axes[2].text(120, 0.2, "Intertidal Flat")
    axes[2].set_xticks([0, s1_d, 50, 100, 150, 200, 250])
    axes[2].xaxis.set_ticklabels([0, "Site 1", 50, 100, 150, 200, 250])
    axes[1].set_ylabel("Elevation [m +MSL]")
    axes[2].set_xlabel("Distance [m]")

    axes[2].get_xticklabels()[1].set_color('red')
    fig.subplots_adjust(
        top=0.88,
        bottom=0.11,
        left=0.215,
        right=0.98,
        hspace=0.2,
        wspace=0.2)
