import datetime
import gc
import matplotlib.cm as cm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from constants import TIMEZONE
from matplotlib.ticker import MultipleLocator
from pandas.plotting import register_matplotlib_converters


WIND_DATA_FILE = "./data/NIWA/2010-2019/FOT wind.csv"
RAINFALL_DATA_FILE = "./data/NIWA/2010-2019/FOT rainfall.csv"
PRESSURE_DATA_FILE = "./data/NIWA/2010-2019/FOT atmospheric pressure.csv"


def plot_wind():
    """
    Plots Wind speed for the months of May and June for the
    2011-2019 period.
    """
    df = pd.read_csv(
        WIND_DATA_FILE,
        usecols=["Date(NZST)", "Dir(DegT)", "Speed(m/s)"],
        index_col=0,
        parse_dates=[0],
        na_values=["", "-"])
    df = df[df.index.year.isin([2011, 2012, 2013, 2014, 2015,
            2016, 2017, 2018, 2019])]
    df = df[df.index.month.isin([5, 6])]

    boxplot_wind(df)
    barplot_wind(df)


def boxplot_wind(df):
    sns.set(rc={"figure.figsize": (12, 6)})
    sns.set_style("white")
    sns.set_style("ticks")
    df['Month'] = df.index.strftime('%b')
    df['Year'] = df.index.strftime('%Y')
    fig, ax = plt.subplots()
    sns.boxplot(x="Year", y="Speed(m/s)", hue="Month", data=df, ax=ax)
    ax.set_ylabel("Wind speed [m/s]")
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.yaxis.set_minor_locator(MultipleLocator(2.5))
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    gc.collect()
    fig.savefig("./plots/weather/windboxplot.png", dpi=300)
    # free mem
    fig.clf()
    plt.close()
    gc.collect()


def barplot_wind(df):
    sns.set(rc={"figure.figsize": (16, 16)})
    sns.set_style("white")
    sns.set_style("ticks")
    fig, axes = plt.subplots(nrows=len(df.index.year.unique()), ncols=1)
    i = 0
    colors = cm.rainbow(np.linspace(0, 1, len(axes)))
    for year, dfy in df.groupby(df.index.year):
        ax = axes[i]
        dfy = dfy.resample("1D").mean()
        ax.bar(
            dfy.index,
            dfy["Speed(m/s)"],
            color=colors[i],
            # s=3,
            label=str(year))
        ax.xaxis.set_tick_params(reset=True)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%B"))
        ax.set_xlim(
            datetime.datetime(year, 5, 1, hour=0,
                              minute=0),
            datetime.datetime(year, 6, 30, hour=23,
                              minute=0))
        if i < len(axes) - 1:
            ax.xaxis.set_visible(False)
            if i == len(axes)//2:
                ax.set_ylabel("Wind speed [m/s]")
        else:
            ax.set_xlabel("Days")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        # ax.spines["left"].set_bounds(0, 20)
        ax.spines["left"].set_position(("outward", 5))
        ax.set_yticks([0, 5, 10])
        i += 1
    fig.legend(title="Years", loc="center right",
               bbox_to_anchor=(0.965, 0.5), ncol=1)
    fig.autofmt_xdate()
    fig.savefig("./plots/weather/windlineplot.png", dpi=300)
    fig.clf()
    plt.close()
    gc.collect()
