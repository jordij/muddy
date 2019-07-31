import dateutil
import gc
import matplotlib.cm as cm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from constants import TIMEZONE, DATES, DATES_FORMAT
from datetime import datetime
from matplotlib.ticker import MultipleLocator
from pandas.plotting import register_matplotlib_converters
from windrose import plot_windrose


WIND_DATA_FILE = "./data/NIWA/2010-2019/FOT wind.csv"
WIND_EXPERIMENT_DATA_FILE = "./data/NIWA/experiment/FOT wind.csv"
RAINFALL_DATA_FILE = "./data/NIWA/2010-2019/FOT rainfall.csv"
PRESSURE_DATA_FILE = "./data/NIWA/2010-2019/FOT atmospheric pressure.csv"
RAINFALL_EXP_DATA_FILE = "./data/NIWA/experiment/FOT rainfall.csv"
RIVERS = {
    "Ohinemuri": "./data/WRC/Ohinemuri_Flow_Karangahake.txt",
    "Piako": "./data/WRC/Piako_Flow_Paeroa-Tahuna.txt",
    "Waihou": "./data/WRC/Waihou_Flow_Te_aroha.txt"
}


def plot_river_flows():
    sns.set(rc={"figure.figsize": (12, 6)})
    sns.set_style("white")
    sns.set_style("ticks")
    fig, ax = plt.subplots()
    for k, v in RIVERS.items():
        df = pd.read_csv(
            v,
            usecols=["Date", "Time", "Flow"],
            parse_dates={"date": ["Date", "Time"]},
            date_parser=lambda d: pd.datetime.strptime(d, '%d/%m/%Y %H:%M:%S'),
            na_values=["GAP"])
        df = df.set_index("date")
        df.index = df.index.tz_localize(TIMEZONE)
        df = df[(df.index >= DATES["start"]) & (df.index <= DATES["end"])]
        df = df.resample("1h").mean()
        ax.plot(
            df.index,
            df["Flow"],
            label=k)
    ax.set_ylabel("Water flow [m^3]")
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%B"))
    ax.set_xlim(df.index.min(), df.index.max())
    ax.set_yticks([0, 25, 50, 100])
    ax.set_xlim(datetime.strptime(DATES["start"], '%Y-%m-%d %H:%M:%S'),
                datetime.strptime(DATES["end"], '%Y-%m-%d %H:%M:%S'))
    sns.despine(right=True, top=True)
    fig.autofmt_xdate()
    fig.show()
    fig.legend()


def plot_rain():
    """
    Plots hourly rainfall for experiment dates.
    """
    df = pd.read_csv(
        RAINFALL_EXP_DATA_FILE,
        usecols=["Date(NZST)", "Amount(mm)"],
        index_col=0,
        parse_dates=[0],
        na_values=["", "-"])
    sns.set(rc={"figure.figsize": (12, 6)})
    sns.set_style("white")
    sns.set_style("ticks")
    fig, ax = plt.subplots()
    ax.bar(
        df.index,
        df["Amount(mm)"],
        width=0.075,
        edgecolor=[])
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%B"))
    ax.set_xlim(datetime.strptime(DATES["start"], DATES_FORMAT),
                datetime.strptime(DATES["end"], DATES_FORMAT))
    sns.despine(right=True, top=True)
    ax.set_yticks(np.arange(0, 16, 2))
    ax.spines["left"].set_bounds(0, 14)
    ax.set_ylabel("Rainfall [mm]")
    fig.autofmt_xdate()
    fig.show()


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
    df["speed"] = df["Speed(m/s)"]
    df["direction"] = df["Dir(DegT)"]
    windrose_plot(df)
    df = df[df.index.year.isin([2011, 2012, 2013, 2014, 2015,
            2016, 2017, 2018, 2019])]
    df = df[df.index.month.isin([5, 6])]
    boxplot_wind(df)
    barplot_wind(df)


def windrose_plot(df):
    """
    Plots windrose for 2017 and experiment dates
    """
    dfnoexp = df[(df.index < DATES["start"]) | (df.index >= DATES["end"])]
    dfexp = df[DATES["start"]:DATES["end"]]
    for d, y in [(dfnoexp, "noexp"), (dfexp, "exp")]:
        ax = plot_windrose(
            d,
            kind='bar',
            normed=True,
            opening=0.8,
            bins=np.arange(0, 14, 2),
            edgecolor="white")
        ax.set_yticks([])
        legend = ax.set_legend(
            bbox_to_anchor=(-0.25, 1),
            title="Wind speed [m/s]",
            loc='upper left')
        labels = [
            u"0 ≤ Ws < 2",
            u"2 ≤ Ws < 4",
            u"4 ≤ Ws < 6",
            u"6 ≤ Ws < 8",
            u"8 ≤ Ws < 10",
            u"10 ≤ Ws < 12",
            u"Ws ≥ 12"]
        for i, l in enumerate(labels):
            legend.get_texts()[i].set_text(l)
        plt.savefig(
            "./plots/weather/rose_%s.png" % y,
            dpi=300,
            bbox_inches='tight')
        plt.close()
        gc.collect()


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


def get_weekly_wind():
    df = pd.read_csv(
        WIND_EXPERIMENT_DATA_FILE,
        usecols=["Date(NZST)", "Dir(DegT)", "Speed(m/s)"],
        index_col=0,
        parse_dates=["Date(NZST)"],
        date_parser=lambda d: pd.datetime.strptime(d, '%d/%m/%Y %H:%M'),
        na_values=["", "-"])
    df["speed"] = df["Speed(m/s)"]
    df["direction"] = df["Dir(DegT)"]
    df.index = df.index.tz_localize(TIMEZONE)
    return [group for i, group in df.groupby(df.index.week)]


def get_weekly_rainfall():
    df = pd.read_csv(
        RAINFALL_EXP_DATA_FILE,
        usecols=["Date(NZST)", "Amount(mm)"],
        index_col=0,
        parse_dates=["Date(NZST)"],
        date_parser=lambda d: pd.datetime.strptime(d, '%d/%m/%Y %H:%M'),
        na_values=["", "-"])
    df["amount"] = df["Amount(mm)"]
    df.index = df.index.tz_localize(TIMEZONE)
    return [group for i, group in df.groupby(df.index.week)]


def get_weekly_pressure():
    df = pd.read_csv(
        PRESSURE_DATA_FILE,
        usecols=["Date(NZST)", "Time(NZST)", "Pmsl(hPa)"],
        parse_dates={"date": ["Date(NZST)", "Time(NZST)"]},
        date_parser=lambda d: pd.datetime.strptime(d, '%d/%m/%Y %H:%M'),
        na_values=["", "-"])
    df["Atmospheric pressure"] = df["Pmsl(hPa)"]
    df = df[(df.date >= DATES["start"]) & (df.date <= DATES["end"])]
    df = df.set_index("date")
    df.index = df.index.tz_localize(TIMEZONE)
    return [group for i, group in df.groupby(df.index.week)]


def get_weekly_rivers():
    rivers = {}
    for k, v in RIVERS.items():
        df = pd.read_csv(
            v,
            usecols=["Date", "Time", "Flow"],
            parse_dates={"date": ["Date", "Time"]},
            date_parser=lambda d: pd.datetime.strptime(d, '%d/%m/%Y %H:%M:%S'),
            na_values=["GAP"])
        df = df.set_index("date")
        df.index = df.index.tz_localize(TIMEZONE)
        df = df[(df.index >= DATES["start"]) & (df.index <= DATES["end"])]
        df = df.resample("1h").mean()
        rivers[k] = [group for i, group in df.groupby(df.index.week)]
    return rivers
