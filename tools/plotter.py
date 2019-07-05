import datetime
import gc
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
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
        sns_plot.axes[1, i].set_xlabel("%s (%s)" % (
            VARIABLES[v]["name"],
            VARIABLES[v]["units"]))
        # sns_plot.axes[1, i].margins(0, 0)
    for i, v in enumerate(yvars):
        sns_plot.axes[i, 0].set_ylabel("%s (%s)" % (
            VARIABLES[v]["name"],
            VARIABLES[v]["units"]))
        # sns_plot.axes[i, 0].margins(0, 0)
    # for axes in sns_plot.axes:
    #     for ax in axes:
    #         ax.margins(0, 0)
    # sns_plot.fig.tight_layout()
    sns_plot.fig.subplots_adjust(top=.95)

    sns_plot.savefig(dest_file, dpi=300)
