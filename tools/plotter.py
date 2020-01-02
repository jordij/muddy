import datetime
import gc
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from collections import OrderedDict
from pandas.plotting import register_matplotlib_converters
from windrose import plot_windrose

from tools import encoder, plot_constants
from constants import OUTPUT_PATH, VARIABLES, INST_TYPES

register_matplotlib_converters()


def plot_obs_calibration():
    """ Plot OBS calibration for all available devices"""
    sns.set(rc={"figure.figsize": (18, 10)})
    sns.set_style("ticks")
    fig, axes = plt.subplots(ncols=len(INST_TYPES), nrows=1)
    for i, t in enumerate(INST_TYPES):
        devs = encoder.create_devices_by_type(t, "h5")
        for d in devs:
            axes[i].plot(
                d.T,
                d.SSC,
                label=d.site,
                marker="o",
                c=plot_constants.colours[d.site])
        axes[i].set(xlabel="Turbidity [NTU]", ylabel="SSC [mg/L]")
        axes[i].spines["top"].set_visible(False)
        axes[i].spines["right"].set_visible(False)
    handles, labels = fig.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(),
               title="Sites", loc="center right")
    dest_file = "%sOBS_calibration.png" % OUTPUT_PATH
    fig.show()
    fig.savefig(dest_file, dpi=200)
    # free mem
    fig.clf()
    plt.close()
    gc.collect()


def plot_all_hourly(dest_file, date, df, vars, minh=0, maxh=24, freqh=1):
    """ Plot given vars from given dataframe and save in dest_file """
    print("Generating %s" % dest_file)
    sns.set(rc={"figure.figsize": (12, 16)})
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
        # give an extra 30mins at boths ends to have some extra margin
        ax.set_xlim(
            datetime.datetime(
                date.year, date.month, date.day, hour=0,
                minute=0, tzinfo=df.index.tz) - pd.Timedelta("30m"),
            datetime.datetime(
                date.year, date.month, date.day, hour=23,
                minute=59, tzinfo=df.index.tz) + pd.Timedelta("30m"))
        # set name and units for each var/axes
        ax.set(xlabel="%s" % str(date), ylabel=vars[i]["units"])
        ax.legend([vars[i]["name"]])
    fig.autofmt_xdate()
    fig.savefig(dest_file, dpi=300)
    # free mem
    fig.clf()
    plt.close()
    gc.collect()


def plot_hourly_ssc_depth_avg(df, date, dest_file, title):
    """ Plot given vars """
    print("Generating %s" % dest_file)
    sns.set(rc={"figure.figsize": (16, 8)})
    fig, axes = plt.subplots(ncols=1, nrows=2, sharex=True)
    fig.suptitle(title)
    df.plot(subplots=True, ax=axes, style=".", legend=None)
    ylabels = ["SSC [mg/l]", "Depth [m]"]
    for i, ax in enumerate(axes):
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M", tz=df.index.tz))
        # give an extra hours at boths ends to have some extra margin
        ax.set_xlim(
            datetime.datetime(
                date.year, date.month, date.day, hour=0,
                minute=0, tzinfo=df.index.tz) - pd.Timedelta("1h"),
            datetime.datetime(
                date.year, date.month, date.day, hour=23,
                minute=59, tzinfo=df.index.tz) + pd.Timedelta("1h"))
        ax.set_ylim(bottom=0)
        ax.tick_params(axis="y", which="major", labelsize=10)
        ax.tick_params(axis="y", which="minor", labelsize=8)
        ax.tick_params(axis="x", which="major", labelsize=8)
        ax.tick_params(axis="x", which="minor", labelsize=6)
        # set name and units for each var/axes
        ax.set(xlabel=str(date), ylabel=ylabels[i])
        # if i == 1:  # depth
        #     ax.axhline(0, ls="--", color="red")
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
    yvars = ["ssc"]
    sns.set_style("white")
    sns.set_style("ticks")
    sns_plot = sns.pairplot(
        df,
        height=8, aspect=1.5,
        x_vars=xvars,
        y_vars=yvars,
        dropna=True)
    sns_plot.fig.suptitle(title)
    for i, v in enumerate(xvars):
        sns_plot.axes[0, i].set_xlabel("%s [%s]" % (
            VARIABLES[v]["name"],
            VARIABLES[v]["units"]))
    for i, v in enumerate(yvars):
        sns_plot.axes[i, 0].set_ylabel("%s [%s]" % (
            VARIABLES[v]["name"],
            VARIABLES[v]["units"]))
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
    sns.set(rc={"figure.figsize": (10, 8)})
    sns.set_style("white")
    sns.set_style("ticks")
    fig, ax = plt.subplots()
    sns.scatterplot(
        "u",
        "ssc",
        data=df,
        alpha=0.75,
        hue="Tide",
        ax=ax)
    ax.set_title(title)
    ax.set_xlabel("%s [%s]" % (
        VARIABLES["u"]["name"],
        VARIABLES["u"]["units"]))
    ax.set_ylabel("%s [%s]" % (
        VARIABLES["ssc"]["name"],
        VARIABLES["ssc"]["units"]))
    sns.despine(right=True, top=True)
    ax.legend(loc='center right', bbox_to_anchor=(1.1, 0.5), ncol=1)
    fig.savefig(dest_file, dpi=300)
    plt.close()
    gc.collect()


def plot_ssc_u_log(df, dest_file, title):
    """
    Plot SSC vs Wave Orbital Velocity
    """
    print("Generating %s" % dest_file)
    sns.set(rc={"figure.figsize": (10, 8)})
    sns.set_style("white")
    sns.set_style("ticks")
    df["ssc"] = np.log10(df["ssc"].astype(float))
    df["u"] = np.power(df["u"], 3)
    fig, ax = plt.subplots()
    sns.scatterplot(
        "u",
        "ssc",
        data=df,
        alpha=0.75,
        hue="Tide",
        ax=ax)
    ax.set_title(title)
    ax.set_xlabel("%s ^3 [%s]" % (
        VARIABLES["u"]["name"],
        VARIABLES["u"]["units"]))
    ax.set_ylabel("%s log 10 [%s]" % (
        VARIABLES["ssc"]["name"],
        VARIABLES["ssc"]["units"]))
    sns.despine(right=True, top=True)
    ax.legend(loc='center right', bbox_to_anchor=(1.1, 0.5), ncol=1)
    ax.set_ylim(bottom=0)
    fig.savefig(dest_file, dpi=300)
    plt.close()
    gc.collect()


def plot_ssc_u_h_series(df, dffl, dest_file, device):
    """
    Plots a combined time series for SSC, Wave Orbital Velocity and water depth
    """
    sns.set(rc={"figure.figsize": (20, 12)})
    # sns.set_style("white")
    sns.set_style("ticks")
    set_font_sizes()
    # plt.figure(figsize=(14, 8))
    # U_ticks = plot_constants.LIMITS[device]["U_ticks"]
    # SSC_ticks = plot_constants.LIMITS[device]["SSC_ticks"]
    U_ticks = plot_constants.COMMON_LIMITS["U_ticks"]
    SSC_ticks = plot_constants.COMMON_LIMITS["SSC_ticks"]
    v_depth = VARIABLES["depth_00"]
    v_ssc = VARIABLES["ssc"]
    v_u = VARIABLES["u"]
    # weekly data
    dflist = [group for group in df.groupby(df.index.week)]
    if dffl is not None:  # floater case
        dffllist = [group for group in dffl.groupby(dffl.index.week)]
    # dflist = [group for group in df.groupby(pd.TimeGrouper(freq='7D'))]
    fig, axes = plt.subplots(ncols=1, nrows=len(dflist))
    i = 0
    for date, dfweek in dflist:
        if dffl is not None:
            datefl, dfweekfl = dffllist[i]
        dfweek["u"] = dfweek["u"].fillna(-1)
        ax = axes[i]
        # water depth
        ax.plot(
            dfweek.index,
            dfweek.depth_00,
            linestyle=":",
            color="black",
            label=v_depth["name"])
        # lims = range(0, int(math.ceil(dfweek.depth_00.max())) + 1)
        # ax.set_ylim(bottom=0, top=5)
        ax.spines["left"].set_position(("outward", -5))
        # ax.spines["left"].set_bounds(0, 5)
        ax.spines["right"].set_visible(False)
        ax.set_yticks([0, 2.5, 5])
        ax.spines["left"].set_bounds(0, 5)
        # time
        axx = plt.gca()
        axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0]))
        axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %Hh",
                                      tz=dfweek.index.tz))
        if i == 2:
            ax.set_ylabel("Depth [%s]" % v_depth["units"])
            ax.yaxis.set_label_coords(-0.025, 1.05)
        # Wave height H
        ax1 = ax.twinx()
        ax1.plot(dfweek.index, dfweek["H"], color="black",
                 label="Significant wave height")
        ax1.yaxis.tick_left()
        # lims = range(0, round(math.ceil(dfweek.H.max()) + 0.1, 1))
        # ax1.set_ylim(bottom=0, top=1)
        ax1.set_yticks([0, 0.5, 1])
        ax1.spines["right"].set_visible(False)
        ax1.spines["top"].set_visible(False)
        ax1.spines["bottom"].set_visible(False)
        ax1.spines["left"].set_position(("outward", 60))
        ax1.spines["left"].set_bounds(0, 1)
        if i == 2:
            ax1.set_ylabel("Significant wave\nheight [%s]" % v_depth["units"])
            ax1.yaxis.set_label_coords(-0.125, 1.05)
        # SSC
        ax2 = ax.twinx()
        ax2.scatter(dfweek.index, dfweek["ssc"], s=3, c="blue",
                    label="%s at seabed" % v_ssc["name"], alpha="0.8")
        ax2.spines["left"].set_visible(False)
        if dffl is not None:
            ax2.scatter(dfweekfl.index, dfweekfl["ssc"], s=3,
                        c="red", label="%s at surface" % v_ssc["name"],
                        alpha="0.8")
        # lims = range(min(SSC_ticks[i]), max(SSC_ticks[i]))
        # ax2.spines["right"].set_bounds(min(SSC_ticks[i]), max(SSC_ticks[i]))
        # ax2.set_yticks(SSC_ticks[i])
        ax2.spines["right"].set_bounds(SSC_ticks[0], SSC_ticks[-1])
        ax2.set_yticks(SSC_ticks)
        ax2.set_ylim(0, None)
        ax2.margins(0, 0)
        if i == 2:
            ax2.set_ylabel("SSC [%s]" % v_ssc["units"])
            ax2.yaxis.set_label_coords(1.045, 1.1)
        # Orbital Vel
        ax3 = ax.twinx()
        ax3.set_ylim(bottom=0)
        ax3.plot(dfweek.index, dfweek["u"], color="green", label=v_u["name"])
        ax3.spines["right"].set_position(("outward", 75))
        ax3.spines["left"].set_visible(False)
        ax3.margins(None, 0)
        # lims = range(min(U_ticks[i]), max(U_ticks[i]))
        # ax3.spines["right"].set_bounds(min(U_ticks[i]), max(U_ticks[i]))
        # ax3.set_yticks(U_ticks[i])
        ax3.spines["right"].set_bounds(U_ticks[0], U_ticks[-1])
        ax3.set_yticks(U_ticks)
        if i == 2:
            ax3.set_ylabel("Wave orbital\nvelocity [%s]" % v_u["units"])
            ax3.yaxis.set_label_coords(1.1, 1.1)
        # cosmetic tweaks
        ax.spines["top"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax3.spines["top"].set_visible(False)
        ax2.spines["bottom"].set_visible(False)
        ax3.spines["bottom"].set_visible(False)
        ax2.xaxis.set_visible(False)
        ax3.xaxis.set_visible(False)

        if i == 0:  # one legend is enough
            fig.legend(loc='lower center', ncol=2, markerscale=4)
        i += 1
    axx = plt.gca()
    axx.xaxis.set_major_locator(mdates.DayLocator())
    axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0]))
    axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %Hh",
                                  tz=df.index.tz))
    fig.subplots_adjust(
        top=0.971,
        bottom=0.229,
        left=0.108,
        right=0.882,
        hspace=0.2,
        wspace=0.2)
    # fig.suptitle(str(device))
    # plt.savefig(dest_file, dpi=300, bbox_inches='tight')
    # free mem
    # fig.show()
    # plt.close()
    # gc.collect()


def plot_ssc_u_h_weekly_series(df, dfl, dfwind, dfrain, dfpressure, dfdepth,
                               dfrivers, dest_file, date, device, wek):
    """
    Plots a combined time series for SSC, Wave Orbital Velocity, water depth
    and a series of environmental variables - rainfall, wind speed, wind dir..
    """
    sns.set(rc={"figure.figsize": (50, 30)})
    sns.set_style("white")
    sns.set_style("ticks")
    set_font_sizes()
    # prepare ticks
    U_ticks = plot_constants.LIMITS[device]["U_ticks"][wek]
    SSC_ticks = plot_constants.LIMITS[device]["SSC_ticks"][wek]
    w_ticks = plot_constants.LIMITS[device]["Wave_ticks"][wek]
    v_depth = VARIABLES["depth_00"]
    v_ssc = VARIABLES["ssc"]
    v_u = VARIABLES["u"]
    fig, axes = plt.subplots(ncols=1, nrows=7, sharex=True)
    # Water depth
    ax = axes[6]
    ax.plot(
        dfdepth.index,
        dfdepth,
        linestyle=":",
        color="black",
        label=v_depth["name"])
    ax.set_ylabel("Depth [%s]" % v_depth["units"])
    lims = range(0, int(math.ceil(dfdepth.max())) + 1)
    ax.set_ylim(bottom=0, top=max(lims))
    ax.spines["left"].set_bounds(min(lims), max(lims))
    # Orb vel
    ax = axes[5]
    df["u"] = df["u"].fillna(-1)
    ax.plot(df.index, df["u"], color="green", label="Wave\norbital velocity")
    ax.set_ylabel("Wave orbital\nvelocity [%s]" % v_u["units"])
    ax.set_ylim(bottom=0, top=df["u"].max())
    lims = range(min(U_ticks), max(U_ticks))
    ax.spines["left"].set_bounds(min(U_ticks), max(U_ticks))
    ax.set_yticks(U_ticks)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False)
    # Wave height
    ax = ax.twinx()
    ax.plot(df.index, df["H"], color="black", label="Significant\nwave height")
    ax.set_ylabel("Significant wave\nheight [%s]" % v_depth["units"])
    ax.set_yticks(w_ticks)
    ax.spines["right"].set_bounds(min(w_ticks), max(w_ticks))
    ax.xaxis.set_visible(False)
    ax.spines["right"].set_position(("outward", 15))
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.35), frameon=False)
    # SSC
    ax = axes[4]
    ax.scatter(df.index, df["ssc"], s=4, c="blue",
               label="%s\nat seabed" % v_ssc["name"], alpha="0.8")
    ax.set_ylabel("SSC [%s]" % v_ssc["units"])
    if dfl is not None:
        ax.scatter(dfl.index, dfl["ssc"], s=4, c="red",
                   label="%s\nat surface" % v_ssc["name"],
                   alpha="0.8")
    lims = range(min(SSC_ticks), max(SSC_ticks))
    ax.spines["left"].set_bounds(min(SSC_ticks), max(SSC_ticks))
    ax.set_yticks(SSC_ticks)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.5), frameon=False)
    # Wind speed and direction
    ax = axes[3]
    ax.scatter(dfwind.index, dfwind["speed"], s=4, c="black",
               label="Wind speed\n[m/s]")
    ax.set_ylabel("Wind speed\n[m/s]")
    ax.set_yticks([0, 7, 14])
    ax.spines["left"].set_bounds(0, 14)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False)
    ax = ax.twinx()
    ax.scatter(dfwind.index, dfwind["direction"],
               marker="x", label="Wind direction\n[degrees]")
    ax.set_ylabel("Wind direction\n[degrees]")
    ax.set_yticks([0, 90, 180, 270, 360])
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.35), frameon=False)
    ax.spines["right"].set_bounds(0, 360)
    ax.xaxis.set_visible(False)
    ax.spines["right"].set_position(("outward", 15))
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    # Rainfall
    ax = axes[2]
    ax.scatter(dfrain.index, dfrain.amount.replace(0, np.nan), s=4, c="black",
               label="Rainfall [mm]")
    ax.set_ylabel("Rainfall\n[mm]")
    ax.set_yticks([0, 5, 10, 15])
    ax.spines["left"].set_bounds(0, 15)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False)
    # Pressure
    ax = ax.twinx()
    ax.plot(dfpressure.index, dfpressure["Atmospheric pressure"],
            label="Atmospheric\npressure [mbar]")
    ax.set_ylabel("Atmospheric\npressure [mbar]")
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.35), frameon=False)
    ax.set_yticks([1006, 1019, 1032])
    ax.spines["right"].set_bounds(1006, 1032)
    ax.xaxis.set_visible(False)
    ax.spines["right"].set_position(("outward", 15))
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    # Salinity
    ax = axes[1]
    ax.plot(df.index, df.salinity_00, c="blue",
            label="Salinity\nat seabed [PSU]")
    if dfl is not None:
        ax.plot(dfl.index, dfl.salinity_00, c="red",
                label="Salinity\nat surface [PSU]")
    ax.set_ylabel("Salinity\n[PSU]")
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.5), frameon=False)
    ax.set_yticks([0, 35])
    ax.spines["left"].set_bounds(0, 35)
    # River flow
    ax = axes[0]
    for river, dfriver in dfrivers:
        ax.plot(dfriver.index, dfriver["Flow"],
                label=river)
    ax.set_yticks([0, 55, 110])
    ax.spines["right"].set_bounds(0, 110)
    ax.set_ylabel("Flow discharge [m^3/s]")
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False)

    for i in range(0, 7, 1):
        axes[i].spines["top"].set_visible(False)
        if i == 6:
            axes[i].xaxis.set_visible(True)
        else:
            axes[i].xaxis.set_visible(False)
            axes[i].spines["bottom"].set_visible(False)
        axes[i].spines["right"].set_visible(False)
        axes[i].set_xlim(
            df.index.min() - pd.Timedelta("3h"), df.index.max())
    # axx = plt.gca()
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
                                 tz=df.index.tz))
    min_date = df.index.min().strftime("%d %b")
    max_date = df.index.max().strftime("%d %b")
    fig.suptitle("%s - Week %d - %s to %s" %
                 (device, wek + 1, min_date, max_date))
    fig.show()
    fig.savefig(dest_file, dpi=600)
    plt.close()
    gc.collect()


def plot_event(title, dfrain, dfrivers, dfpressure, dfwind, df, dfl):
    sns.set(rc={"figure.figsize": (12, 16)})
    sns.set_style("white")
    sns.set_style("ticks")
    # set_font_sizes()
    # prepare ticks
    # U_ticks = plot_constants.LIMITS[device]["U_ticks"][wek]
    # SSC_ticks = plot_constants.LIMITS[device]["SSC_ticks"][wek]
    # w_ticks = plot_constants.LIMITS[device]["Wave_ticks"][wek]
    v_depth = VARIABLES["depth_00"]
    v_ssc = VARIABLES["ssc"]
    v_u = VARIABLES["u"]
    fig, axes = plt.subplots(ncols=1, nrows=7)
    # WATER DEPTH
    ax = axes[6]
    ax.plot(
        df.index,
        df.depth_00,
        linestyle=":",
        color="black",
        label=v_depth["name"])
    ax.set_ylabel("Depth [%s]" % v_depth["units"])
    lims = range(0, int(math.ceil(df.depth_00.max())) + 1)
    # ax.set_ylim(bottom=0, top=max(lims))
    ax.spines["left"].set_bounds(0, 5)
    ax.set_yticks([0, 2.5, 5])
    # ORBITAL VELOCITY
    ax = axes[5]
    df["u"] = df["u"].fillna(-10)
    ax.scatter(df.index, df["u"], s=3, color="green",
               label="Wave\norbital velocity")
    ax.set_ylabel("Wave orbital\nvelocity [%s]" % v_u["units"])
    ax.set_ylim(bottom=0, top=df["u"].max())
    # lims = range(min(U_ticks), max(U_ticks))
    ax.spines["left"].set_bounds(0, 90)
    ax.set_yticks([0, 45, 90])
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.7), frameon=False, labelspacing=1)
    # WAVE HEIGHT
    ax = ax.twinx()
    ax.plot(df.index, df["H"], color="black", label="Significant\nwave height")
    ax.set_ylabel("Significant wave\nheight [%s]" % v_depth["units"])
    ax.set_yticks([0, 0.5, 1])
    ax.spines["right"].set_bounds(0, 1)
    ax.xaxis.set_visible(False)
    ax.spines["right"].set_position(("outward", 15))
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.3), frameon=False, labelspacing=1)
    # SSC
    ax = axes[4]
    ax.scatter(df.index, df["ssc"], s=4, c="blue",
               label="%s\nat seabed" % v_ssc["name"], alpha="0.8")
    ax.set_ylabel("SSC [%s]" % v_ssc["units"])
    if dfl is not None:
        ax.scatter(dfl.index, dfl["ssc"], s=4, c="red",
                   label="%s\nat surface" % v_ssc["name"],
                   alpha="0.8")
    ax.spines["right"].set_visible(False)
    # lims = range(min(SSC_ticks), max(SSC_ticks))
    ax.spines["left"].set_bounds(0, 3600)
    ax.set_yticks([0, 1500, 3600])
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.5), frameon=False, labelspacing=1)
    # WIND SPEED AND DIR
    ax = axes[3]
    ax.scatter(dfwind.index, dfwind["speed"], s=4, c="black",
               label="Wind speed\n[m/s]")
    ax.set_ylabel("Wind speed\n[m/s]")
    ax.set_yticks([0, 7, 14])
    ax.spines["left"].set_bounds(0, 14)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.7), frameon=False, labelspacing=1)
    ax = ax.twinx()
    ax.scatter(dfwind.index, dfwind["direction"],
               marker="x", label="Wind direction\n[degrees]")
    ax.set_ylabel("Wind direction\n[degrees]")
    ax.set_yticks([0, 90, 180, 270, 360])
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.3), frameon=False, labelspacing=1)
    ax.spines["right"].set_bounds(0, 360)
    ax.xaxis.set_visible(False)
    ax.spines["right"].set_position(("outward", 15))
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    # RAINFALL
    ax = axes[2]
    ax.scatter(dfrain.index, dfrain.amount.replace(0, np.nan), s=4, c="black",
               label="Rainfall [mm]")
    ax.set_ylabel("Rainfall\n[mm]")
    ax.set_yticks([0, 5, 10, 15])
    ax.spines["left"].set_bounds(0, 15)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False, labelspacing=1)
    # ATM PRESSURE
    ax = ax.twinx()
    ax.plot(dfpressure.index, dfpressure["Atmospheric pressure"],
            label="Atmospheric\npressure [mbar]")
    ax.set_ylabel("Atmospheric\npressure [mbar]")
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.35), frameon=False, labelspacing=1)
    ax.set_yticks([1006, 1019, 1032])
    ax.spines["right"].set_bounds(1006, 1032)
    ax.xaxis.set_visible(False)
    ax.spines["right"].set_position(("outward", 15))
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    # SALINITY
    ax = axes[1]
    ax.plot(df.index, df.salinity_00, c="blue",
            label="Salinity\nat seabed [PSU]")
    if dfl is not None:
        ax.plot(dfl.index, dfl.salinity_00, c="red",
                label="Salinity\nat surface [PSU]")
    ax.set_ylabel("Salinity\n[PSU]")
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.5), frameon=False, labelspacing=1)
    ax.set_yticks([0, 35])
    ax.spines["left"].set_bounds(0, 35)
    # RIVERS FLOW-DISCHARGE
    ax = axes[0]
    for river, dfriver in dfrivers.items():
        ax.plot(dfriver.index, dfriver["Flow"],
                label=river)
    ax.set_yticks([0, 55, 110])
    ax.spines["left"].set_bounds(0, 110)
    ax.set_ylabel("Flow discharge [m^3/s]")
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False, labelspacing=1)

    for i in range(0, 7, 1):
        axes[i].spines["top"].set_visible(False)
        if i == 6:
            axes[i].xaxis.set_visible(True)
        else:
            axes[i].xaxis.set_visible(False)
            axes[i].spines["bottom"].set_visible(False)
        axes[i].spines["right"].set_visible(False)
        axes[i].set_xlim(df.index.min() - pd.Timedelta("1h"), df.index.max())
    axx = plt.gca()
    axx.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    axx.xaxis.set_major_formatter(mdates.DateFormatter(
                                  "%H:%M", tz=df.index.tz))
    fig.suptitle(title)
    fig.show()
    # fig.savefig(dest_file, dpi=300)
    # del fig
    # plt.close()
    # gc.collect()


def plot_presentation_ssc_event(devs, floaters, dfwind, dfrain, dfpress, title):
    sns.set(rc={"figure.figsize": (30, 15)})
    sns.set_style("ticks")
    set_font_sizes(big=False)
    u_max = max([d["u"].max() for d in devs])
    depth_max = max([d["depth_00"].max() for d in devs])
    fig, axes = plt.subplots(ncols=1, nrows=2+len(devs), sharex=True)

    # Pressure + rain
    ax = axes[0]
    ax.bar(dfrain.index, dfrain.amount.replace(0, np.nan),
           width=0.025, label="Rainfall [mm]")
    ax.set_ylabel("Rainfall\n[mm]")
    ax.set_yticks([0, 5, 10, 15])
    ax.spines["left"].set_bounds(-1, 16)
    ax = ax.twinx()
    ax.plot(dfpress.index, dfpress["Atmospheric pressure"],
            label="P [mbar]")
    ax.set_ylabel("P [mbar]")
    ax.set_yticks([1006, 1019, 1032])
    ax.spines["right"].set_bounds(1006, 1032)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Wind
    ax = axes[1]
    ax.scatter(dfwind.index, dfwind["speed"], s=10, c="black",
               label="Wind\nspeed\n[m/s]")
    ax.set_ylabel("Wind\nspeed\n[m/s]")
    ax.set_yticks([0, 7, 14])
    ax.spines["left"].set_bounds(0, 14)
    ax = ax.twinx()
    ax.scatter(dfwind.index, dfwind["direction"], s=15,
               marker="x", label="Wind\ndirection\n[°]")
    ax.set_ylabel("Wind\n direction\n[°]")
    ax.set_yticks([0, 90, 180, 270, 360])

    i = 2
    for d in devs:
        floater = floaters[i-2]
        axes[i].plot(
            d.index,
            d["u"],
            label="Wave orbital velocity [cm/s]",
            c="green")
        axes[i].set_ylim(0, math.ceil(u_max))
        axes[i].set_yticks([0, 45])
        axes[i].spines["top"].set_visible(False)
        axes[i].set_ylabel("Usig [cm/s]")

        wov = axes[i].twinx()
        wov.set_ylim(0, 1)
        wov.set_yticks([0, 1])
        wov.plot(
            d.index,
            d["H"],
            label="H [m]",
            c="blue")
        wov.spines["top"].set_visible(False)
        wov.set_ylabel("H [m]")

        wd = axes[i].twinx()
        wd.tick_params(axis='y', which='right', labelleft=False, labelright=True)
        wd.set_ylim(0, 5.5)
        wd.set_yticks([0, 5.5])
        wd.spines["top"].set_visible(False)
        wd.spines["right"].set_position(("outward", 80))
        wd.plot(
            d.index,
            d["depth_00"],
            linestyle="--",
            c="black")
        wd.set_ylabel("h [m]")

        conc = axes[i].twinx()
        # conc.tick_params(axis='y', which='right', labelleft=False, labelright=True)
        conc.spines["right"].set_position(("outward", 160))
        conc.set_yticks([0, 200])
        conc.set_ylim(-5, 225)
        conc.scatter(
            d.index,
            d.ssc,
            label="SSC - bed [mg/L]",
            c="blue",
            s=10)
        if floater is not None:
            conc.scatter(
                floater.index,
                floater.ssc,
                label="SSC - surface [mg/L]",
                c="red",
                s=20)
        conc.set_ylabel("SSC\n[mg/L]")

        i += 1
    axes[5].xaxis.set_major_locator(mdates.HourLocator(interval=12))
    axes[5].xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %Hh",
                                      tz=devs[2].index.tz))
    axes[6].set_xlabel("Date")
    fig.subplots_adjust(
        left=0.065,
        right=0.815,
    )
    fig.savefig("./supertest.png", dpi=300)
    # ax.yaxis.set_label_coords(-0.035, 1.1)
    # ax.legend(title="Sites")
    # fig.suptitle(title)
    # fig.show()
    # gc.collect()


def plot_event_ssc_series(devices, title):
    sns.set(rc={"figure.figsize": (15, 10)})
    # sns.set_style("white")
    sns.set_style("ticks")
    set_font_sizes(big=True)
    v_ssc = VARIABLES["ssc"]
    colours = {
        "S1": "red",
        "S2": "steelblue",
        "S3": "limegreen",
        "S4": "orange",
        "S5": "purple",
    }
    fig, ax = plt.subplots()
    for d in devices:
        ax.scatter(
            d.df_avg.index,
            d.df_avg.ssc,
            label=d.site,
            s=20,
            c=colours[d.site])
    # ax.set_xlim(
    #         devices[0].df_avg.index.min() - pd.Timedelta("3h"), devices[0].df_avg.index.max())
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %Hh",
                                 tz=devices[0].df_avg.index.tz))
    ax.set_ylabel("SSC [%s]" % v_ssc["units"])
    ax.set_xlabel("Date")
    # ax.yaxis.set_label_coords(-0.035, 1.1)
    ax.legend(title="", frameon=False)
    # fig.suptitle(title)
    # fig.show()
    gc.collect()


def set_font_sizes(big=True):
    if big:
        SMALL_SIZE = 18  # 18
        MEDIUM_SIZE = 28
        BIGGER_SIZE = 28
    else:
        SMALL_SIZE = 14
        MEDIUM_SIZE = 18
        BIGGER_SIZE = 22

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    sns.axes_style({
        'axes.edgecolor': '1',
        'axes.labelcolor': '1',
        'grid.color': '1',
        'text.color': '1',
        'xtick.color': '1',
        'ytick.color': '1'})


def plot_ssc_series(devices):
    sns.set(rc={"figure.figsize": (14, 10)})
    sns.set_style("white")
    sns.set_style("ticks")
    v_ssc = VARIABLES["ssc"]
    colours = {
        "S1": "red",
        "S2": "blue",
        "S3": "green",
        "S4": "black",
        "S5": "purple",
    }
    ddict = {}
    for d in devices:
        for gdate, df in d.df_avg.groupby(d.df_avg.index.week):
            if d.site not in ddict:
                ddict[d.site] = []
            ddict[d.site].append(df)
    fig, axes = plt.subplots(ncols=1, nrows=4)  # 4 weeks
    j = 0
    for key, val in ddict.items():
        i = 0
        for df in val:
            axes[i].scatter(df.index, df.ssc, label=key,
                            s=5, alpha=0.8, c=colours[key])
            if j == 0:
                # time
                axes[i].xaxis.set_major_locator(
                    mdates.HourLocator(byhour=[0, 12]))
                axes[i].xaxis.set_major_formatter(
                    mdates.DateFormatter("%d-%m %H:%M", tz=df.index.tz))
            i += 1
        j += 1
    # one axis label and legend enough
    axes[2].set_ylabel("SSC [%s]" % v_ssc["units"])
    axes[2].yaxis.set_label_coords(-0.035, 1.1)
    axes[2].legend(title="Sites", bbox_to_anchor=(1.1, 1.35))


def plot_ssc_heatmap(devices, start=None, end=None):
    sns.set(rc={"figure.figsize": (12, 20)})
    # sns.set_style("white")
    sns.set_style("ticks")
    set_font_sizes(big=True)
    v_ssc = VARIABLES["ssc"]
    # values = {"ssc": 2115}
    # devices[0].df_avg = devices[0].df_avg.fillna(value=values)
    # merge SSC from all devices into a single df
    df_merged = devices[0].df_avg
    for i in range(1, len(devices)):
        suffix = "_%s" % devices[i].site
        df_merged = df_merged.join(devices[i].df_avg,
                                   how="outer",
                                   rsuffix=suffix)
        df_merged[devices[i].site] = df_merged["ssc%s" % suffix]
    df_merged[devices[0].site] = df_merged["ssc"]
    # df_ssc = np.log10(df_merged[[d.site for d in devices]].astype(float))
    df_ssc = df_merged[[d.site for d in devices]].astype(float)
    vmax = df_ssc[[d.site for d in devices]].max().max()
    vmin = df_ssc[[d.site for d in devices]].min().min()
    if start is not None and end is not None:
        df_ssc = df_ssc[start:end]
        vmax = df_ssc[[d.site for d in devices]].max().max()
        vmin = df_ssc[[d.site for d in devices]].min().min()
        fig, ax = plt.subplots(figsize=(10, 10))
        # NORMAL VERSION
        df_ssc.index = df_ssc.index.strftime('%d-%m %H:%M')
        ax = sns.heatmap(df_ssc.T, vmin=vmin, vmax=3600, cmap='RdYlBu_r',
                         square=False, xticklabels=36, yticklabels=True,
                         linewidths=.0, ax=ax)
        # ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
        # ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H"))
        fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
        for label in ax.get_ymajorticklabels():
            label.set_rotation(90)
        # fig.xticks(rotation=70)
        ax.set_ylabel("Site")
        ax.set_xlabel("Date")
        # ax.tick_params(axis="y", which="major", labelsize=9)
        # ax.tick_params(axis="x", which="major", labelsize=9)
        # POSTER VERSION
        # df_ssc.index = df_ssc.index.strftime('%H:%M')
        # sns.heatmap(df_ssc.T, vmin=vmin, vmax=3600, cmap='RdYlBu_r', ax=ax,
        #             square=False, xticklabels=24, yticklabels=True,
        #             linewidths=.1, cbar_kws={'label': 'SSC [mg/L]', "ticks": [0, 1200, 2400, 3600]})
        # ax.tick_params(axis="y", which="both", left=False, right=False)
        # ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        # ax.tick_params(axis="x", which="both", left=False, right=False)
        # ax.yaxis.set_visible(False)
        # ax.xaxis.set_visible(False)
        # ax.spines["bottom"].set_visible(False)
        # ax.spines["left"].set_visible(False)
    else:
        fig, axes = plt.subplots(ncols=1, nrows=4, figsize=(28, 4))
        cbar_ax = fig.add_axes([0.925, .108, .01, .8])
        i = 0
        for date, df in df_ssc.groupby(df_ssc.index.week):
            tzinfo = df.index.tz
            df.index = df.index.strftime('%d-%m %Hh')
            sns.heatmap(df.T, vmin=0, vmax=vmax, cmap='RdYlBu_r',
                        ax=axes[i], xticklabels=72, yticklabels=True,
                        linewidths=.0, cbar=(i == 0),
                        cbar_ax=cbar_ax if i == 0 else None)
            axes[i].tick_params(axis="y", which="major", labelsize=14)
            axes[i].tick_params(axis="x", which="major", labelsize=14)
            # axes[i].set_xlim(df.index.min(),
            #                  df.index.max())
            # axes[i].xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
            # axes[i].xaxis.set_major_formatter(
            #     mdates.DateFormatter("%d-%m %H:%M", tz=tzinfo))
            i += 1
        cbar_ax.set_ylabel("SSC [%s]" % v_ssc["units"])

    # fig.set_size_inches(12, 8) # POSTER
    # fig.tight_layout()
    # fig.subplots_adjust(
    #     top=0.975,
    #     bottom=0.045,
    #     left=0.036,
    #     right=0.897,
    #     hspace=0.261,
    #     wspace=0.2)
    # fig.show()
    # if start is not None and end is not None:
    #     i = 0
    #     while i < len(devices):
    #         fig2, axes2 = plt.subplots(ncols=1, nrows=1)
    #         subdf = devices[i].df_avg[start:end]
    #         axes2.plot(subdf.index, subdf.depth_00, color="black")
    #         # axes2.spines["bottom"].set_visible(False)
    #         # axes2.yaxis.set_visible(False)
    #         # axes2.xaxis.set_visible(False)
    #         axes2.spines["top"].set_visible(False)
    #         # axes2.spines["left"].set_visible(False)
    #         maxd = int(math.ceil(subdf.depth_00.max()))
    #         axes2.set_ylim(bottom=0, top=maxd)
    #         # ax.spines["left"].set_position(("outward", -5))
    #         # axes2.spines["left"].set_bounds(min(lims), max(lims))
    #         axes2.set_yticks([0, maxd])
    #         axes2.set_xticks([])
    #         axes2.yaxis.tick_right()
    #         axes2.xaxis.set_major_locator(
    #                 mdates.HourLocator(interval=1))
    #         axes2.xaxis.set_major_formatter(
    #             mdates.DateFormatter("%H:%M", tz=subdf.index.tz))
    #         i += 1
    #         fig2.set_size_inches(9, 2.75)
    #         fig2.tight_layout()
    #         fig2.show()
    #         fig2.savefig("./stormwd_%d.png" % i, dpi=600,
    #                      bbox_inches='tight', transparent=True)


def plot_salinities(floaters, bedframes):
    """
    Plot weekly salinity levels for all instruments/sites.
    """
    sns.set(rc={"figure.figsize": (14, 10)})
    # sns.set_style("white")
    sns.set_style("ticks")
    set_font_sizes()
    v_ssc = VARIABLES["ssc"]
    colours = {
        "S1": "red",
        "S2": "blue",
        "S3": "green",
        "S4": "black",
        "S5": "purple",
    }
    # Bedframes in one fig
    fig, axes = plt.subplots(ncols=1, nrows=4)  # 4 weeks
    for d in bedframes:
        i = 0
        for gdate, df in d.df_avg.groupby(d.df_avg.index.week):
            ax = axes[i]
            ax.plot(df.index, df.salinity_00, label=d.site, c=colours[d.site])
            ax.set_yticks([0, 20, 35])
            i += 1
    # one axis label and legend enough
    axes[2].set_ylabel("Salinty [PSU]")
    axes[3].set_xlabel("Date")
    axes[2].yaxis.set_label_coords(-0.035, 1.1)
    axes[3].legend(title=None, ncol=5, loc='lower center')
    # Floaters in anoter fig
    fig2, axes2 = plt.subplots(ncols=1, nrows=4)  # 4 weeks
    for d in floaters:
        i = 0
        for gdate, df in d.df_avg.groupby(d.df_avg.index.week):
            ax = axes2[i]
            ax.plot(df.index, df.salinity_00, label=d.site, c=colours[d.site])
            ax.set_yticks([0, 20, 35])
            i += 1
    # one axis label and legend enough
    axes2[2].set_ylabel("Salinty [PSU]")
    axes2[3].set_xlabel("Date")
    axes2[2].yaxis.set_label_coords(-0.035, 1.1)
    axes2[3].legend(title=None, loc='lower center', ncol=4)


def plot_timeseries_flux(dbf):
    sns.set(rc={"figure.figsize": (20, 12)})
    sns.set_style("ticks")
    set_font_sizes(big=False)
    fig, axes = plt.subplots(ncols=1, nrows=4)
    i = 0
    vmin = dbf.Q.min()
    vmax = dbf.Q.max()
    lims = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    for date, dfweek in [group for group in dbf.groupby(dbf.index.week)]:
        ax = axes[i]
        ax.scatter(
            dfweek.index,
            dfweek["Q"],
            color="green",
            s=7,
            label="Q [kg/m^2/s]")
        ax.set_yticks([0, 0.05, 0.1, 0.15])
        ax.set_ylim(vmin-0.025, 0.175)
        ax1 = ax.twinx()
        grouped = dfweek.groupby('Tide')
        j = 0
        colours = ["red", "blue"]
        for key, group in grouped:
            ax1.scatter(group.index, group["Q_dir"], s=7,
                        label="Q direction\n%s [ ° ]" % key,
                        color=colours[j])
            j += 1
        ax1.set_yticks([0, 90, 180, 270, 360])
        if i == 1:  # one legend is enough
            ax.legend(loc="center left", markerscale=4,
                      bbox_to_anchor=(-0.255, 0.65), frameon=False)
            ax1.legend(loc="center left", markerscale=4,
                       bbox_to_anchor=(-0.255, 0.05), frameon=False)
            ax.set_ylabel("Q [kg/m^2/s]")
            ax1.set_ylabel("Q direction [ ° ]")
            ax.yaxis.set_label_coords(-0.045, -0.25)
            ax1.yaxis.set_label_coords(1.0395, -0.2)
        elif i == 3:
            ax.set_xlabel("Date")
        ax1.spines["bottom"].set_visible(False)
        ax1.xaxis.set_visible(False)
        ax = ax.twinx()
        ax.plot(dfweek.index, dfweek["Vel_Mag"], label="Velocity\nmagnitude\n[m/s]",
                c="black")
        ax.spines["right"].set_position(("outward", 65))
        ax.set_ylim(bottom=0, top=max(lims))
        ax.spines["left"].set_bounds(min(lims), max(lims))
        ax.spines["bottom"].set_visible(False)
        ax.xaxis.set_visible(False)
        if i == 1:
            ax.set_ylabel("Velocity magnitude [m/s]")
            ax.yaxis.set_label_coords(1.095, -0.15)
            ax.legend(loc="center left", markerscale=4,
                      bbox_to_anchor=(-0.255, -0.65), frameon=False)
        i += 1
        axx = plt.gca()
        axx.xaxis.set_major_locator(mdates.DayLocator())
        axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0]))
        axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %Hh",
                                      tz=dbf.index.tz))
    fig.tight_layout()
    fig.subplots_adjust(
        top=0.971,
        bottom=0.087,
        left=0.184,
        right=0.908,
        hspace=0.2,
        wspace=0.2)
    gc.collect()


def plot_total_fluxes(fluxes):
    sns.set(rc={"figure.figsize": (12, 16)})
    sns.set_style("ticks")
    set_font_sizes(big=True)
    colours = [
        "red",
        "steelblue",
        "limegreen",
        "orange",
        "purple",
    ]
    fig, ax = plt.subplots()
    i = 0

    # SUM
    # for site in fluxes:
    #     df = site.groupby(site.index.date)["Q"].sum() # sum or cumsum
    #     ax.plot(df.index, df.values, '-o', color=colours[i],
    #             label="Site %d" % (i + 1))
    #     i += 1
    # ENDSUM

    # CUMSUM
    for site in fluxes:
        df = site.groupby(site.index.date)["Q"].sum() # sum or cumsum
        df = pd.DataFrame({"Q": df.values}, index=df.index)
        df = df.cumsum()
        ax.plot(df.index, df.Q, '-o', color=colours[i],
                label="Site %d" % (i + 1))
        i += 1
    # ENDCUMSUM

    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))
    ax.set_xlim(fluxes[0].index.min(), fluxes[0].index.max())
    ax.set_ylabel("Q [kg/m^2]")
    ax.set_xlabel("Date")
    ax.legend(markerscale=4, frameon=False, loc="center left",
              bbox_to_anchor=(-0.275, 0.5))
    ax.axhline(0, ls="--", color="grey")
    fig.autofmt_xdate()
    fig.subplots_adjust(
        top=0.925,
        bottom=0.138,
        left=0.225,
        right=0.983,
        hspace=0.2,
        wspace=0.2)


def plot_flux_windrose(dbf, filename):
    # Plot flux rose
    sns.set(rc={"figure.figsize": (30, 16)})
    sns.set_style("ticks")
    set_font_sizes(big=True)
    bins = list(np.arange(0, 0.1, 0.01))
    bins.insert(1, 0.005)
    ax = plot_windrose(dbf, kind='bar', bins=bins,
                       normed=True, opening=0.8,
                       var_name="Q", direction_name="Q_dir")
    # TRANSPARENT
    ax.set_yticks([])  # remove % labels
    # ax.get_legend().remove()
    plt.axis('off')
    legend = ax.set_legend(bbox_to_anchor=(-1, -1))
    # ENDOF TRANSPARENT

    # legend = ax.set_legend(
    #     bbox_to_anchor=(-0.275, 0.2),
    #     frameon=False,
    #     # loc='upper left',
    #     title="Q [kg/m^2/s]")
    # labels = [
    #     u"0 ≤ Q < 0.005",
    #     u"0.005 ≤ Q < 0.01",
    #     u"0.01 ≤ Q < 0.02",
    #     u"0.02 ≤ Q < 0.03",
    #     u"0.03 ≤ Q < 0.04",
    #     u"0.04 ≤ Q < 0.05",
    #     u"0.05 ≤ Q < 0.06",
    #     u"0.06 ≤ Q < 0.07",
    #     u"0.07 ≤ Q < 0.08",
    #     u"0.08 ≤ Q < 0.09",
    #     u"Q ≥ 0.09"]
    # for i, l in enumerate(labels):
    #     legend.get_texts()[i].set_text(l)
    plt.savefig("./plots/fluxes/flux_scale_transparent_%s" % filename,
                dpi=300, transparent=True)


def plot_depth(df):
    sns.set_style("ticks")
    set_font_sizes()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(df.index, df.depth_00)
    plt.xlabel("Date")
    plt.ylabel("Depth [m]")


def get_depth(row):
    """
    Get signed difference, in seconds, between row index (name)
    and given mid_value timestamp
    """
    if row.depth_00 < 0.25:
        return "< 0.25 m"
    elif row.depth_00 < 0.5:
        return "< 0.5 m"
    elif row.depth_00 < 0.75:
        return "< 0.75 m"
    elif row.depth_00 < 1:
        return "< 1 m"
    elif row.depth_00 < 1.5:
        return "< 1.5 m"
    elif row.depth_00 < 2:
        return "< 2 m"
    elif row.depth_00 < 3:
        return "< 3 m"
    elif row.depth_00 < 4:
        return "< 4 m"
    else:
        return "> 4 m"


def plot_ssc_vs_u(df):
    sns.set_style("ticks", {
        "figure.figsize": (10, 10)})
    set_font_sizes()
    df["Depth [m]"] = df.apply(lambda r: get_depth(r), axis=1)
    sizes = {
        "< 0.25 m": 50,
        "< 0.5 m": 70,
        "< 0.75 m": 90,
        "< 1 m": 110,
        "< 1.5 m": 140,
        "< 2 m": 160,
        "< 3 m": 200,
        "< 4 m": 250,
        "> 4 m": 300,
    }
    size_order = sizes.keys()
    # ax = sns.scatterplot(x="u", y="ssc", hue="site",
                        # size="depth_00", sizes=(60, 300),
                        # legend="brief", alpha=0.8, data=df)
    # ax.set_xlabel("Wave orbital velocity [cm/s]")
    # ax.set_ylabel("SSC [mg/L]")
    # palette = sns.light_palette("navy", as_cmap=True)
    g = sns.relplot(x="u", y="ssc", hue="Tide",
                    alpha=0.5, size="Depth [m]", sizes=sizes,
                    col="site", data=df, size_order=size_order, s=100)
    g.set_axis_labels("Wave orbital\nvelocity [cm/s]", "SSC [mg/L]")


def plot_tidal_hex_u_ssc(df, intervals=None):

    sns.set_style("ticks", {
        "figure.figsize": (10, 10),
        "axes.facecolor": "#f7fbff"})
    set_font_sizes()
    # HEX bivariate plot
    g = sns.jointplot(x="hours", y="ssc", data=df, kind="hex", cmap='Blues',
                      xlim=(-6, 6), ylim=(0, int(df["ssc"].max())),
                      dropna=True)
    g.ax_joint.set_xticks([-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6])
    g.set_axis_labels("Hours before and after high tide", "SSC [mg/L]")
    g.fig.subplots_adjust(wspace=.0, hspace=0.)
    g.ax_marg_x.set_facecolor("white")
    g.ax_marg_y.set_facecolor("white")
    g.fig.subplots_adjust(
        top=0.9,
        bottom=0.2,
        left=0.2,
        right=0.9,
        hspace=0.0,
        wspace=0.0)


def plot_tidal_reg_u_ssc(df, intervals=None):
    # Regression plots
    sns.set_style("ticks", {
        "figure.figsize": (12, 10)})
    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=False)

    sns.regplot(x="hours", y="ssc", data=df, order=2,
                ci=95, scatter_kws={"s": 40}, ax=axes[0])
    axes[0].set_ylabel('SSC [mg/L]')
    axes[0].set_xlabel(None)
    axes[0].set_xticks([-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6])
    axes[0].set_yticks([0, 100, 200])

    sns.regplot(x="hours", y="u", data=df, order=2,
                ci=95, scatter_kws={"s": 40}, ax=axes[1])
    axes[1].set_ylabel('Wave orbital\nvelocity [cm/s]')
    axes[1].set_xlabel('Hours before and after high tide')
    axes[1].set_xticks([-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6])
    axes[1].set_yticks([0, 25, 50, 75, 100])
    axes[1].set_ylim(bottom=0, top=110)
    fig.subplots_adjust(
        top=0.9,
        bottom=0.2,
        left=0.2,
        right=0.9,
        hspace=0.1,
        wspace=0.0)


def plot_detailed_interval(df, dfwind):
    sns.set_style("ticks", {
        "figure.figsize": (12, 10)})
    fig, axes = plt.subplots(nrows=4, ncols=1, sharex=True)

    ax = axes[3]
    ax.scatter(dfwind.index, dfwind["speed"], s=4, c="black",
               label="Wind speed\n[m/s]")
    ax.set_ylabel("Wind speed\n[m/s]")
    ax.set_yticks([0, 7, 14])
    ax.spines["left"].set_bounds(0, 14)

    ax = ax.twinx()
    ax.scatter(dfwind.index, dfwind["direction"],
               marker="x", label="Wind direction\n[degrees]")
    ax.set_ylabel("Wind direction\n[degrees]")
    ax.set_yticks([0, 90, 180, 270, 360])

    ax = axes[2]
