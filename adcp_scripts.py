import matplotlib.pyplot as plt

from adcp import Aquadopp, RDI, Signature1000
from constants import CALM_EVENT_DATES, STORM_TIDES, CALM_TIDES
from tools import encoder


def plot_depths():
    s1 = Aquadopp(1)
    s2 = Aquadopp(2)
    s3 = Aquadopp(3)
    s4 = Signature1000(4)
    s5 = RDI(5)
    fig, ax = plt.subplots()
    for s in [s1, s2, s3, s4, s5]:
        # df = s.wd["2017-05-17 06:00:00+12:00":"2017-05-17 16:00:00+12:00"]
        df = s.wd[CALM_EVENT_DATES["start"]:CALM_EVENT_DATES["end"]]
        ax.plot(df.index, df["WaterDepth"], label=str(s))
        fig.legend()


def plot_weekly_depths():
    concertos = encoder.create_devices_by_type("bedframe", "h5")
    aqs = [Aquadopp(1), Aquadopp(2), Aquadopp(3), Signature1000(4), RDI(5)]
    weeks = aqs[0].df.index.get_level_values('Date').week
    fig, axes = plt.subplots(ncols=1, nrows=4, figsize=(28, 4))
    i = 0
    for week, df in aqs[0].df.groupby(weeks):
        for a in aqs:
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


def plot_intervals():
    s1 = Aquadopp(1)
    s2 = Aquadopp(2)
    s3 = Aquadopp(3)
    s4 = Signature1000(4)
    s5 = RDI(5)
    for s in [s1, s2, s3, s4, s5]:
        s.plot_interval(
            CALM_TIDES["flood"][s.site-1]["start"],
            CALM_TIDES["flood"][s.site-1]["bursts"])
        if CALM_TIDES["peak"][s.site-1]:
            s.plot_interval(
                CALM_TIDES["peak"][s.site-1]["start"],
                CALM_TIDES["peak"][s.site-1]["bursts"])
        s.plot_interval(
            CALM_TIDES["ebb"][s.site-1]["start"],
            CALM_TIDES["ebb"][s.site-1]["bursts"])
