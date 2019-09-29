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
    sns.set_style("white")
    sns.set_style("ticks")
    # plt.figure(figsize=(14, 8))
    U_ticks = plot_constants.LIMITS[device]["U_ticks"]
    SSC_ticks = plot_constants.LIMITS[device]["SSC_ticks"]
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
        # time
        axx = plt.gca()
        axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
        axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
                                      tz=dfweek.index.tz))
        if i == 2:
            ax.set_ylabel("Depth [%s]" % v_depth["units"])
            ax.yaxis.set_label_coords(-0.015, 1.05)
        # Wave height H
        ax1 = ax.twinx()
        ax1.plot(dfweek.index, dfweek["H"], color="black",
                 label="Significant wave height")
        ax1.yaxis.tick_left()
        # lims = range(0, round(math.ceil(dfweek.H.max()) + 0.1, 1))
        ax1.set_ylim(bottom=0, top=1)
        ax1.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
        ax1.spines["right"].set_visible(False)
        ax1.spines["top"].set_visible(False)
        ax1.spines["bottom"].set_visible(False)
        ax1.spines["left"].set_position(("outward", 40))
        ax1.spines["left"].set_bounds(0, 1)
        if i == 2:
            ax1.set_ylabel("Significant wave height [%s]" % v_depth["units"])
            ax1.yaxis.set_label_coords(-0.075, 1.05)
        # SSC
        ax2 = ax.twinx()
        ax2.scatter(dfweek.index, dfweek["ssc"], s=3, c="blue",
                    label="%s at seabed" % v_ssc["name"], alpha="0.8")
        ax2.spines["left"].set_visible(False)
        if dffl is not None:
            ax2.scatter(dfweekfl.index, dfweekfl["ssc"], s=3,
                        c="red", label="%s at surface" % v_ssc["name"],
                        alpha="0.8")
        lims = range(min(SSC_ticks[i]), max(SSC_ticks[i]))
        ax2.spines["right"].set_bounds(min(SSC_ticks[i]), max(SSC_ticks[i]))
        ax2.set_yticks(SSC_ticks[i])
        if i == 2:
            ax2.set_ylabel("SSC [%s]" % v_ssc["units"])
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
            ax3.set_ylabel("Wave orbital velocity[%s]" % v_u["units"])
            ax3.yaxis.set_label_coords(1.075, 1.1)
        # cosmetic tweaks
        ax.spines["top"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax3.spines["top"].set_visible(False)
        ax2.spines["bottom"].set_visible(False)
        ax3.spines["bottom"].set_visible(False)
        ax2.xaxis.set_visible(False)
        ax3.xaxis.set_visible(False)

        if i == 0:  # one legend is enough
            ax.figure.legend()
        i += 1

    axx = plt.gca()
    axx.xaxis.set_major_locator(mdates.DayLocator())
    axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
                                  tz=df.index.tz))
    fig.suptitle(str(device))
    plt.savefig(dest_file, dpi=300, bbox_inches='tight')
    # free mem
    # fig.show()
    plt.close()
    gc.collect()


def plot_ssc_u_h_weekly_series(df, dfl, dfwind, dfrain, dfpressure, dfdepth,
                               dfrivers, dest_file, date, device, wek):
    """
    Plots a combined time series for SSC, Wave Orbital Velocity, water depth
    and a series of environmental variables - rainfall, wind speed, wind dir..
    """
    sns.set(rc={"figure.figsize": (20, 12)})
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
    fig, axes = plt.subplots(ncols=1, nrows=7)
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
    ax.plot(df.index, df.salinity_00, c="blue", label="Salinity\nat seabed [PSU]")
    if dfl is not None:
        ax.plot(dfl.index, dfl.salinity_00, c="red", label="Salinity\nat surface [PSU]")
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
    ax.set_ylabel("Water flow [m^3]")
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
    axx = plt.gca()
    axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
                                  tz=df.index.tz))
    min_date = df.index.min().strftime("%d %b")
    max_date = df.index.max().strftime("%d %b")
    fig.suptitle("%s - Week %d - %s to %s" %
                 (device, wek + 1, min_date, max_date))
    fig.show()
    fig.savefig(dest_file, dpi=300)
    plt.close()
    gc.collect()


def plot_event(title, dfrain, dfrivers, dfpressure, dfwind, df, dfl):
    sns.set(rc={"figure.figsize": (12, 16)})
    sns.set_style("white")
    sns.set_style("ticks")
    set_font_sizes()
    # prepare ticks
    # U_ticks = plot_constants.LIMITS[device]["U_ticks"][wek]
    # SSC_ticks = plot_constants.LIMITS[device]["SSC_ticks"][wek]
    # w_ticks = plot_constants.LIMITS[device]["Wave_ticks"][wek]
    v_depth = VARIABLES["depth_00"]
    v_ssc = VARIABLES["ssc"]
    v_u = VARIABLES["u"]
    fig, axes = plt.subplots(ncols=1, nrows=7)
    # Water depth
    ax = axes[6]
    ax.plot(
        df.index,
        df.depth_00,
        linestyle=":",
        color="black",
        label=v_depth["name"])
    ax.set_ylabel("Depth [%s]" % v_depth["units"])
    lims = range(0, int(math.ceil(df.depth_00.max())) + 1)
    ax.set_ylim(bottom=0, top=max(lims))
    ax.spines["left"].set_bounds(min(lims), max(lims))
    # Orb vel
    ax = axes[5]
    df["u"] = df["u"].fillna(-10)
    ax.scatter(df.index, df["u"], s=3, color="green", label="Wave\norbital velocity")
    ax.set_ylabel("Wave orbital\nvelocity [%s]" % v_u["units"])
    ax.set_ylim(bottom=0, top=df["u"].max())
    # lims = range(min(U_ticks), max(U_ticks))
    # ax.spines["left"].set_bounds(min(U_ticks), max(U_ticks))
    # ax.set_yticks(U_ticks)
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False)
    # Wave height
    ax = ax.twinx()
    ax.plot(df.index, df["H"], color="black", label="Significant\nwave height")
    ax.set_ylabel("Significant wave\nheight [%s]" % v_depth["units"])
    # ax.set_yticks(w_ticks)
    # ax.spines["right"].set_bounds(min(w_ticks), max(w_ticks))
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
    # lims = range(min(SSC_ticks), max(SSC_ticks))
    # ax.spines["left"].set_bounds(min(SSC_ticks), max(SSC_ticks))
    # ax.set_yticks(SSC_ticks)
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
    ax.plot(df.index, df.salinity_00, c="blue", label="Salinity\nat seabed [PSU]")
    if dfl is not None:
        ax.plot(dfl.index, dfl.salinity_00, c="red", label="Salinity\nat surface [PSU]")
    ax.set_ylabel("Salinity\n[PSU]")
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.5), frameon=False)
    ax.set_yticks([0, 35])
    ax.spines["left"].set_bounds(0, 35)
    # River flow
    ax = axes[0]
    for river, dfriver in dfrivers.items():
        ax.plot(dfriver.index, dfriver["Flow"],
                label=river)
    # ax.set_yticks([0, 55, 110])
    # ax.spines["right"].set_bounds(0, 110)
    ax.set_ylabel("Water flow [m^3]")
    ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False)

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
    axx.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=df.index.tz))
    fig.suptitle(title)
    fig.show()
    # fig.savefig(dest_file, dpi=300)
    # plt.close()
    # gc.collect()


def plot_event_ssc_series(devices, title):
    sns.set(rc={"figure.figsize": (20, 10)})
    sns.set_style("white")
    sns.set_style("ticks")
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
            s=10,
            c=colours[d.site])
    # ax.set_xlim(
    #         devices[0].df_avg.index.min() - pd.Timedelta("3h"), devices[0].df_avg.index.max())
    # ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6]))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M",
    #                              tz=devices[0].df_avg.index.tz))
    ax.set_ylabel("SSC [%s]" % v_ssc["units"])
    # ax.yaxis.set_label_coords(-0.035, 1.1)
    ax.legend(title="Sites")
    fig.suptitle(title)
    fig.show()
    gc.collect()


def set_font_sizes():
    SMALL_SIZE = 28
    MEDIUM_SIZE = 28
    BIGGER_SIZE = 28

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


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
    fig.show()
    gc.collect()


def plot_ssc_heatmap(devices, start=None, end=None):
    sns.set_style("white")
    sns.set_style("ticks")
    v_ssc = VARIABLES["ssc"]
    values = {"ssc": 2115}
    devices[0].df_avg = devices[0].df_avg.fillna(value=values)
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
        # df_ssc.index = df_ssc.index.strftime('%d-%m %H:%M')
        # sns.heatmap(df_ssc.T, vmin=vmin, vmax=vmax, cmap='RdYlBu_r', ax=ax,
        #             square=False, xticklabels=36, yticklabels=True,
        #             linewidths=.0)
        # ax.tick_params(axis="y", which="major", labelsize=9)
        # ax.tick_params(axis="x", which="major", labelsize=9)
        # POSTER VERSION
        df_ssc.index = df_ssc.index.strftime('%H:%M')
        sns.heatmap(df_ssc.T, vmin=vmin, vmax=3600, cmap='RdYlBu_r', ax=ax,
                    square=False, xticklabels=24, yticklabels=True,
                    linewidths=.1, cbar_kws={'label': 'SSC [mg/L]', "ticks": [0, 1200, 2400, 3600]})
        ax.tick_params(axis="y", which="both", left=False, right=False)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        ax.tick_params(axis="x", which="both", left=False, right=False)
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
    else:
        fig, axes = plt.subplots(ncols=1, nrows=4, figsize=(28, 4))
        cbar_ax = fig.add_axes([0.925, .108, .01, .8])
        i = 0
        for date, df in df_ssc.groupby(df_ssc.index.week):
            tzinfo = df.index.tz
            df.index = df.index.strftime('%d-%m %H:%M')
            sns.heatmap(df.T, vmin=vmin, vmax=1000, cmap='RdYlBu_r',
                        ax=axes[i], xticklabels=72, yticklabels=True,
                        linewidths=.0, cbar=(i == 0),
                        cbar_ax=cbar_ax if i == 0 else None)
            axes[i].tick_params(axis="y", which="major", labelsize=9)
            axes[i].tick_params(axis="x", which="major", labelsize=9)
            # axes[i].set_xlim(df.index.min(),
            #                  df.index.max())
            # axes[i].xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
            # axes[i].xaxis.set_major_formatter(
            #     mdates.DateFormatter("%d-%m %H:%M", tz=tzinfo))
            i += 1
        cbar_ax.set_ylabel("SSC [%s]" % v_ssc["units"])

    # fig.set_size_inches(12, 8) # POSTER
    fig.tight_layout()
    fig.show()
    if start is not None and end is not None:
        i = 0
        while i < len(devices):
            fig2, axes2 = plt.subplots(ncols=1, nrows=1)
            subdf = devices[i].df_avg[start:end]
            axes2.plot(subdf.index, subdf.depth_00, color="black")
            # axes2.spines["bottom"].set_visible(False)
            # axes2.yaxis.set_visible(False)
            # axes2.xaxis.set_visible(False)
            axes2.spines["top"].set_visible(False)
            # axes2.spines["left"].set_visible(False)
            maxd = int(math.ceil(subdf.depth_00.max()))
            axes2.set_ylim(bottom=0, top=maxd)
            # ax.spines["left"].set_position(("outward", -5))
            # axes2.spines["left"].set_bounds(min(lims), max(lims))
            axes2.set_yticks([0, maxd])
            axes2.set_xticks([])
            axes2.yaxis.tick_right()
            axes2.xaxis.set_major_locator(
                    mdates.HourLocator(interval=1))
            axes2.xaxis.set_major_formatter(
                mdates.DateFormatter("%H:%M", tz=subdf.index.tz))
            i += 1
            fig2.set_size_inches(9, 2.75)
            fig2.tight_layout()
            fig2.show()
            fig2.savefig("./stormwd_%d.png" % i, dpi=600,
                         bbox_inches='tight', transparent=True)
