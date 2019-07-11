import datetime
import gc
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters

from tools import encoder
from constants import OUTPUT_PATH, VARIABLES, INST_TYPES

register_matplotlib_converters()


def plot_obs_calibration():
    """ Plot OBS calibration for all available devices"""
    sns.set(rc={"figure.figsize": (9, 8)})
    for t in INST_TYPES:
        devs = encoder.create_devices_by_type(t)
        fig, ax = plt.subplots()
        for d in devs:
            ax.plot(d.T, d.SSC, label=d.site, marker='o')
        ax.set(xlabel="Turbidity [NTU]", ylabel="SSC [mg/L]")
        fig.legend(title='Sites', loc="center right")
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
    yvars = ["ssc", "ssc_sd"]
    sns.set(rc={"figure.figsize": (8, 8)})
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
        sns_plot.axes[1, i].set_xlabel("%s [%s]" % (
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
    sns.set(rc={"figure.figsize": (8, 8)})
    sns_plot = sns.scatterplot(
        "u",
        "ssc",
        data=df,
        alpha=0.5,
        hue="Tide")
    ax = plt.gca()
    ax.set_title(title)
    ax.set_xlabel("%s [%s]" % (
        VARIABLES["u"]["name"],
        VARIABLES["u"]["units"]))
    ax.set_ylabel("%s [%s]" % (
        VARIABLES["ssc"]["name"],
        VARIABLES["ssc"]["units"]))
    plt.savefig(dest_file, dpi=300)
    # free mem
    plt.close()
    gc.collect()


def plot_ssc_u_h_series(df, dest_file, title):
    """
    Plots a combined time series for SSC, Wave Orbital Velocity and water depth
    """
    # sns.set(rc={"figure.figsize": (8, 4)})
    custom_ssc_ticks = [
        [0, 500, 1000, 1500],
        [0, 50, 100, 150, 200],
        [0, 50, 100, 150, 200],
        [0, 10, 15, 20]
    ]
    custom_u_ticks = [
        [0, 10, 20, 30, 40, 50, 60],
        [0, 5, 10, 15, 20, 25],
        [0, 5, 10, 15, 20],
        [0, 2, 4, 6, 8]
    ]
    plt.rcParams['axes.facecolor'] = 'white'
    dflist = [group for group in df.groupby(df.index.week)]
    # dflist = [group for group in df.groupby(pd.TimeGrouper(freq='7D'))]

    fig, axes = plt.subplots(ncols=1, nrows=4, sharex=False)
    i = 0
    # for j in range(0, 4):
    for j in range(1, 5):
        date, dfweek = dflist[j]
        ax = axes[i]
        # water depth
        ax.plot(dfweek.index, dfweek.depth_00, linestyle=":", color="black", label=VARIABLES["depth_00"]["name"])
        # ax.xaxis.set_major_locator(mdates.DayLocator())
        # ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        # ax.fmt_xdata = mdates.DateFormatter("%d/%m", tz=dfweek.index.tz)

        ax.spines['left'].set_position(('outward', 5))
        lims = range(0, int(round(df.depth_00.max())))
        ax.spines['left'].set_bounds(min(lims), max(lims))
        ax.spines['right'].set_visible(False)
        ax.set_yticks(lims)
        # ax.set_xticklabels(dfweek.index.day_name().unique())
        axx = plt.gca()
        axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
        axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M", tz=dfweek.index.tz))
        print(ax.get_xticks())
        ax.spines["bottom"].set_bounds(min(ax.get_xticks()), max(ax.get_xticks()))
        # ax.xaxis.set_major_locator(mdates.DayLocator())
        # ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d", tz=dfweek.index.tz))
        # # ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        # ax.set_yticks(dfweek.index.)
        # TODO fix left Y line

        # plt.setp(ax.get_xticklines()[-2:], visible=False)
        # SSC
        ax2 = ax.twinx()
        ax2.scatter(dfweek.index, dfweek["ssc"], s=5, c="blue", label=VARIABLES["ssc"]["name"])
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_position(('outward', 5))
        lims = range(min(custom_ssc_ticks[i]), max(custom_ssc_ticks[i]))
        ax2.spines['right'].set_bounds(min(custom_ssc_ticks[i]), max(custom_ssc_ticks[i]))
        ax2.set_yticks(custom_ssc_ticks[i])
        if i == 2:
            ax2.set_ylabel("[%s]" % VARIABLES["ssc"]["units"])
            ax2.yaxis.set_label_coords(1.035, 1.1)
        # Orbital Vel
        ax3 = ax.twinx()
        ax3.plot(dfweek.index, dfweek["u"], color="green", label=VARIABLES["u"]["name"])
        ax3.spines['right'].set_position(('outward', 55))
        ax3.spines['left'].set_visible(False)
        lims = range(min(custom_u_ticks[i]), max(custom_u_ticks[i]))
        ax3.spines['right'].set_bounds(min(custom_u_ticks[i]), max(custom_u_ticks[i]))
        ax3.set_yticks(custom_u_ticks[i])

        if i == 2:
            ax3.set_ylabel("[%s]" % VARIABLES["u"]["units"])
            ax3.yaxis.set_label_coords(1.075, 1.1)

        ax.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax3.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax3.spines['bottom'].set_visible(False)
        ax2.xaxis.set_visible(False)
        ax3.xaxis.set_visible(False)

        ax.grid(False)
        ax2.grid(False)
        ax3.grid(False)
        if i == 0:  # one legend is enough
            ax.figure.legend()
        i += 1

    axx = plt.gca()
    axx.xaxis.set_major_locator(mdates.DayLocator())
    axx.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    axx.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M", tz=df.index.tz))

    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
    plt.ylabel("[%s]" % VARIABLES["depth_00"]["units"])
    fig.show()
