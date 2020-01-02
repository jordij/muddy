import matplotlib.pyplot as plt

from adcp import Aquadopp, RDI, Signature1000
from constants import CALM_EVENT_DATES, STORM_TIDES, CALM_TIDES
from tools import encoder


def get_adcps():
    """
    Return array of ADCPs
    """
    return [Aquadopp(1),
            Aquadopp(2),
            Aquadopp(3),
            Signature1000(4),
            RDI(5)]


def plot_depths(adcps):
    """
    Depth plotter
    """
    fig, ax = plt.subplots()
    for s in adcps:
        # df = s.wd["2017-05-17 06:00:00+12:00":"2017-05-17 16:00:00+12:00"]
        df = s.wd[CALM_EVENT_DATES["start"]:CALM_EVENT_DATES["end"]]
        ax.plot(df.index, df["WaterDepth"], label=str(s))
        fig.legend()


def plot_weekly_depths(adcps):
    """
    Weekly depth plotter
    """
    concertos = encoder.create_devices_by_type("bedframe", "h5")
    adcps = [Aquadopp(1), Aquadopp(2), Aquadopp(3), Signature1000(4), RDI(5)]
    weeks = adcps[0].df.index.get_level_values('Date').week
    fig, axes = plt.subplots(ncols=1, nrows=4, figsize=(28, 4))
    i = 0
    for week, df in adcps[0].df.groupby(weeks):
        for a in adcps:
            df = a.wd[a.wd.index.week == week]
            axes[i].plot(df.index, df["WaterDepth"], label=str(a))
        i += 1
    weeks = concertos[0].df_avg.index.week
    i = 0
    for week, df in concertos[0].df_avg.groupby(weeks):
        for c in concertos:
            df = c.df_avg[c.df_avg.index.week == week]
            axes[i].plot(df.index, df["depth_00"], label=str(c), linestyle=":")
        i += 1
    axes[2].legend()


def plot_intervals(adcps):
    """
    Plot velocity profile by defined intervals
    """
    for s in adcps:
        s.plot_interval(
            STORM_TIDES["flood"][s.site-1]["start"],
            STORM_TIDES["flood"][s.site-1]["bursts"])
        if STORM_TIDES["peak"][s.site-1]:
            s.plot_interval(
                STORM_TIDES["peak"][s.site-1]["start"],
                STORM_TIDES["peak"][s.site-1]["bursts"])
        s.plot_interval(
            STORM_TIDES["ebb"][s.site-1]["start"],
            STORM_TIDES["ebb"][s.site-1]["bursts"])


def stats(adcps):
    """
    Basic mean stats for ADCPs
    """
    for s in adcps:
        print(s.site)
        sdf = s.df[s.df.Vel_Mag > .000000000000000000]
        print(sdf.Vel_Mag.min())
        print(sdf.Vel_Mag.max())
        print(sdf.Vel_Mag.mean())


def plot_tidal_N(adcps):
    """
    N vel component plotter
    """
    for s in adcps:
        s.plot_mean_velocity()
