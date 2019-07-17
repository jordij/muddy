import datetime
import gc
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters

from tools import encoder, plot_constants
from constants import OUTPUT_PATH, VARIABLES, INST_TYPES

register_matplotlib_converters()


def plot_obs_calibration():
    """ Plot OBS calibration for all available devices"""
    sns.set_style("white")
    sns.set_style("ticks")
    plt.figure(figsize=(9, 8))
    for t in INST_TYPES:
        devs = encoder.create_devices_by_type(t, "h5")
        fig, ax = plt.subplots()
        for d in devs:
            ax.plot(d.T, d.SSC, label=d.site, marker="o")
        ax.set(xlabel="Turbidity [NTU]", ylabel="SSC [mg/L]")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.legend(title="Sites", loc="center right")
        dest_file = "%sOBS_calib_%s.png" % (OUTPUT_PATH, t)
        fig.savefig(dest_file, dpi=200)
        # free mem
        fig.clf()
        plt.close()
        gc.collect()


def plot_all_hourly(dest_file, date, df, vars, minh=0, maxh=24, freqh=1):
    """ Plot given vars from given dataframe and save in dest_file """
    print("Generating %s" % dest_file)
    sns.set(rc={"figure.figsize": (8, 12)})
    fig, axes = plt.subplots(ncols=1, nrows=len(vars), sharex=True)
    df.plot(subplots=True, linewidth=0.25, ax=axes)
    for i, ax in enumerate(axes):
        ax.xaxis.set_major_locator(
            mdates.HourLocator(byhour=range(minh, maxh, freqh)))
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M", tz=df.index.tz))
        ax.tick_params(axis="y", which="major", labelsize=10)
        ax.tick_params(axis="y", which="minor", labelsize=8)
        ax.tick_params(axis="x", which="major", labelsize=10)
        ax.tick_params(axis="x", which="minor", labelsize=8)
        # set name and units for each var/axes
        ax.set(xlabel="%s" % str(date), ylabel=vars[i]["units"])
        ax.legend([vars[i]["name"]])
    fig.autofmt_xdate()
    plt.savefig(dest_file, dpi=300)
    # free mem
    fig.clf()
    plt.close()
    gc.collect()


def plot_hourly_turb_depth_avg(df, date, dest_file, title):
    """ Plot given vars """
    print("Generating %s" % dest_file)
    sns.set(rc={"figure.figsize": (8, 8)})
    fig, axes = plt.subplots(ncols=1, nrows=2, sharex=True)
    fig.suptitle(title)
    df.plot(subplots=True, ax=axes, style=".", legend=None)
    ylabels = ["Turbidity [NTU]", "Depth [m]"]
    for i, ax in enumerate(axes):
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M", tz=df.index.tz))
        # always X ticks from 00h to 23h
        ax.set_xlim(
            datetime.datetime(date.year, date.month, date.day, hour=0,
                              minute=0, tzinfo=df.index.tz),
            datetime.datetime(date.year, date.month, date.day, hour=23,
                              minute=0, tzinfo=df.index.tz))
        ax.tick_params(axis="y", which="major", labelsize=10)
        ax.tick_params(axis="y", which="minor", labelsize=8)
        ax.tick_params(axis="x", which="major", labelsize=10)
        ax.tick_params(axis="x", which="minor", labelsize=8)
        # set name and units for each var/axes
        ax.set(xlabel=str(date), ylabel=ylabels[i])
        if i == 1:  # depth
            ax.axhline(0, ls="--", color="red")
    fig.autofmt_xdate()
    plt.savefig(dest_file, dpi=300)
    # free mem
    fig.clf()
    plt.close()
    gc.collect()


def plot_ssc_avg(df, dest_file, title):
    """ Plot SSC vs Salinity and Depth """
    print("Generating %s" % dest_file)
    xvars = ["depth_00", "salinity_00"]
    # yvars = ["ssc", "ssc_sd"]
    yvars = ["ssc"]
    sns.set_style("white")
    sns.set_style("ticks")
    plt.figure(figsize=(8, 8))
    sns_plot = sns.pairplot(
        df,
        height=8, aspect=1.5,
        kind="reg",
        plot_kws={"line_kws": {"color": "red"}},
        x_vars=xvars,
        y_vars=yvars,
        dropna=True)
    sns_plot.fig.suptitle(title)
    for i, v in enumerate(xvars):
        sns_plot.axes[0, i].set_xlabel("%s [%s]" % (
            VARIABLES[v]["name"],
            VARIABLES[v]["units"]))
        # sns_plot.axes[1, i].margins(0, 0)
    for i, v in enumerate(yvars):
        sns_plot.axes[i, 0].set_ylabel("%s [%s]" % (
            VARIABLES[v]["name"],
            VARIABLES[v]["units"]))
        # sns_plot.axes[i, 0].margins(0, 0)
    # for axes in sns_plot.axes:
    #     for ax in axes:
    #         ax.margins(0, 0)
    # sns_plot.fig.tight_layout()
    sns_plot.fig.subplots_adjust(top=.95)
    sns_plot.savefig(dest_file, dpi=300)
    # free mem
    sns_plot.fig.clf()
    plt.close()
    gc.collect()


def plot_ssc_u(df, dest_file, title):
    """
    Plot SSC vs Wave Orbital Velocity
    """
    print("Generating %s" % dest_file)
    sns.set_style("white")
    sns.set_style("ticks")
    plt.figure(figsize=(10, 8))
    sns_plot = sns.scatterplot(
        "u",
        "ssc",
        data=df,
        alpha=0.75,
        hue="Tide")
    ax = plt.gca()
    ax.set_title(title)
    ax.set_xlabel("%s [%s]" % (
        VARIABLES["u"]["name"],
        VARIABLES["u"]["units"]))
    ax.set_ylabel("%s [%s]" % (
        VARIABLES["ssc"]["name"],
        VARIABLES["ssc"]["units"]))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc='center right', bbox_to_anchor=(1.1, 0.5), ncol=1)
    plt.savefig(dest_file, dpi=300)
    # free mem
    plt.close()
    gc.collect()


def plot_ssc_u_h_series(df, dffl, dest_file, dev):
    """
    Plots a combined time series for SSC, Wave Orbital Velocity and water depth
    """
    sns.set_style("white")
    sns.set_style("ticks")
    # plt.figure(figsize=(14, 8))
    # plot cosmetic vars
    U_ticks = plot_constants.LIMITS[dev]["U_ticks"]
    SSC_ticks = plot_constants.LIMITS[dev]["SSC_ticks"]
    # plt.rcParams["axes.facecolor"] = "white"
    v_depth = VARIABLES["depth_00"]
    v_ssc = VARIABLES["ssc"]
    v_u = VARIABLES["u"]
    # weekly data
    dflist = [group for group in df.groupby(df.index.week)]
    if dffl is not None:
        dffllist = [group for group in dffl.groupby(dffl.index.week)]
    # dflist = [group for group in df.groupby(pd.TimeGrouper(freq='7D'))]
    fig, axes = plt.subplots(ncols=1, nrows=4)
    i = 0
    # for j in range(0, 4):
    for j in range(1, 5):
        date, dfweek = dflist[j]
        if dffl is not None:
            datefl, dfweekfl = dffllist[j]
        # dfweek_clean = dfweek.dropna(subset=["u"])
        dfweek["u"] = dfweek["u"].fillna(-1)
        ax = axes[i]
        # water depth
        ax.plot(
            dfweek.index,
            dfweek.depth_00,
            linestyle=":",
            color="black",
            label=v_depth["name"])
        lims = range(0, int(math.ceil(dfweek.depth_00.max())) + 1)
        ax.set_ylim(bottom=0, top=max(lims))
        ax.spines["left"].set_position(("outward", -5))
        ax.spines["left"].set_bounds(min(lims), max(lims))
        ax.spines["right"].set_visible(False)
        ax.set_yticks(lims)
        # ax.tick_params(axis="x", length=0.5, color="black")
        # ax.spines["bottom"].set_bounds(ax.get_xticks()[0], ax.get_xticks()[1])
        # time
        axx = plt.gca()
        axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
        axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
                                      tz=dfweek.index.tz))
        if i == 2:
            ax.set_ylabel("[%s]" % v_depth["units"])
            ax.yaxis.set_label_coords(-0.025, 1.05)
        # SSC
        ax2 = ax.twinx()
        ax2.scatter(dfweek.index, dfweek["ssc"], s=3, c="blue",
                    label="%s at seabed" % v_ssc["name"], alpha="0.8")
        ax2.spines["left"].set_visible(False)
        if dffl is not None:
            ax2.scatter(dfweekfl.index, dfweekfl["ssc"], s=3,
                        c="red", label="%s at surface" % v_ssc["name"],
                        alpha="0.8")
        # ax2.spines["right"].set_position(("outward", 5))
        lims = range(min(SSC_ticks[i]), max(SSC_ticks[i]))
        ax2.spines["right"].set_bounds(min(SSC_ticks[i]), max(SSC_ticks[i]))
        ax2.set_yticks(SSC_ticks[i])
        if i == 2:
            ax2.set_ylabel("[%s]" % v_ssc["units"])
            ax2.yaxis.set_label_coords(1.035, 1.1)
        # Orbital Vel
        ax3 = ax.twinx()
        ax3.set_ylim(bottom=0, top=max(dfweek["u"]))
        ax3.plot(dfweek.index, dfweek["u"], color="green", label=v_u["name"])
        ax3.spines["right"].set_position(("outward", 55))
        ax3.spines["left"].set_visible(False)
        lims = range(min(U_ticks[i]), max(U_ticks[i]))
        ax3.spines["right"].set_bounds(min(U_ticks[i]), max(U_ticks[i]))
        ax3.set_yticks(U_ticks[i])

        if i == 2:
            ax3.set_ylabel("[%s]" % v_u["units"])
            ax3.yaxis.set_label_coords(1.075, 1.1)

        ax.spines["top"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax3.spines["top"].set_visible(False)
        ax2.spines["bottom"].set_visible(False)
        ax3.spines["bottom"].set_visible(False)
        ax2.xaxis.set_visible(False)
        ax3.xaxis.set_visible(False)

        # ax.grid(False)
        # ax2.grid(False)
        # ax3.grid(False)
        if i == 0:  # one legend is enough
            ax.figure.legend()
        i += 1

    axx = plt.gca()
    axx.xaxis.set_major_locator(mdates.DayLocator())
    axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
                                  tz=df.index.tz))
    # plt.savefig(dest_file, dpi=200, bbox_inches='tight')
    # free mem
    fig.show()
    # plt.close()
    gc.collect()


def plot_ssc_u_h_series_v2(df, dffl, dest_file, dev):
    """
    Plots a combined time series for SSC, Wave Orbital Velocity and water depth
    """
    sns.set_style("white")
    sns.set_style("ticks")
    # plt.figure(figsize=(14, 8))
    # plot cosmetic vars
    U_ticks = plot_constants.LIMITS[dev]["U_ticks"]
    SSC_ticks = plot_constants.LIMITS[dev]["SSC_ticks"]
    # plt.rcParams["axes.facecolor"] = "white"
    v_depth = VARIABLES["depth_00"]
    v_ssc = VARIABLES["ssc"]
    v_u = VARIABLES["u"]
    # weekly data
    dflist = [group for group in df.groupby(df.index.week)]
    dffllist = [group for group in dffl.groupby(dffl.index.week)]
    # dflist = [group for group in df.groupby(pd.TimeGrouper(freq='7D'))]
    fig, axes = plt.subplots(ncols=1, nrows=4)
    i = 0
    # for j in range(0, 4):
    for j in range(1, 5):
        date, dfweek = dflist[j]
        datefl, dfweekfl = dffllist[j]



        # dfweek_clean = dfweek.dropna(subset=["u"])
        dfweek["u"] = dfweek["u"].fillna(-1)
        ax = axes[i]
        # water depth
        ax.plot(
            dfweek.index,
            dfweek.depth_00,
            linestyle=":",
            color="black",
            label=v_depth["name"])
        lims = range(0, int(math.ceil(dfweek.depth_00.max())) + 1)
        ax.set_ylim(bottom=0, top=max(lims))
        ax.spines["left"].set_position(("outward", -5))
        ax.spines["left"].set_bounds(min(lims), max(lims))
        ax.spines["right"].set_visible(False)
        ax.set_yticks(lims)
        # ax.tick_params(axis="x", length=0.5, color="black")
        # ax.spines["bottom"].set_bounds(ax.get_xticks()[0], ax.get_xticks()[1])
        # time
        axx = plt.gca()
        axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
        axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
                                      tz=dfweek.index.tz))
        if i == 2:
            ax.set_ylabel("[%s]" % v_depth["units"])
            ax.yaxis.set_label_coords(-0.025, 1.05)
        # SSC
        ax2 = ax.twinx()
        ax2.scatter(dfweek.index, dfweek["ssc"], s=3, c="blue",
                    label="%s at seabed" % v_ssc["name"], alpha="0.8")
        ax2.spines["left"].set_visible(False)
        ax2.scatter(dfweekfl.index, dfweekfl["ssc"], s=3, c="red",
                    label="%s at surface" % v_ssc["name"], alpha="0.8")
        # ax2.spines["right"].set_position(("outward", 5))
        lims = range(min(SSC_ticks[i]), max(SSC_ticks[i]))
        ax2.spines["right"].set_bounds(min(SSC_ticks[i]), max(SSC_ticks[i]))
        ax2.set_yticks(SSC_ticks[i])
        if i == 2:
            ax2.set_ylabel("[%s]" % v_ssc["units"])
            ax2.yaxis.set_label_coords(1.035, 1.1)
        # Orbital Vel
        ax3 = ax.twinx()
        ax3.set_ylim(bottom=0, top=max(dfweek["u"]))
        ax3.plot(dfweek.index, dfweek["u"], color="green", label=v_u["name"])
        ax3.spines["right"].set_position(("outward", 55))
        ax3.spines["left"].set_visible(False)
        lims = range(min(U_ticks[i]), max(U_ticks[i]))
        ax3.spines["right"].set_bounds(min(U_ticks[i]), max(U_ticks[i]))
        ax3.set_yticks(U_ticks[i])

        if i == 2:
            ax3.set_ylabel("[%s]" % v_u["units"])
            ax3.yaxis.set_label_coords(1.075, 1.1)

        ax.spines["top"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax3.spines["top"].set_visible(False)
        ax2.spines["bottom"].set_visible(False)
        ax3.spines["bottom"].set_visible(False)
        ax2.xaxis.set_visible(False)
        ax3.xaxis.set_visible(False)

        # ax.grid(False)
        # ax2.grid(False)
        # ax3.grid(False)
        if i == 0:  # one legend is enough
            ax.figure.legend()
        i += 1

    axx = plt.gca()
    axx.xaxis.set_major_locator(mdates.DayLocator())
    axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
                                  tz=df.index.tz))
    # plt.savefig(dest_file, dpi=200, bbox_inches='tight')
    # free mem
    fig.show()
    # plt.close()
    gc.collect()
