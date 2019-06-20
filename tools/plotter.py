import datetime
import gc
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import register_matplotlib_converters

from tools import encoder
from constants import (DEVICES, OUTPUT_PATH, PLOT_VARS, VARIABLES, AVG_FOLDER,
                       MIN_DEPTH, MIN_TURB, INST_TYPES)

register_matplotlib_converters()


def plot_all_days(origin, site="all"):
    """ Plot all vars in a daily plot for all sites """
    sns.set(rc={"figure.figsize": (12, 12)})
    if site == "all":  # all instruments
        for d in DEVICES:
            df = encoder.get_df(d, origin)
            dflist = [group for group in df.groupby(df.index.date)]
            nvars = encoder.get_df_nvars(df)
            for date, dfday in dflist:
                dest_file = "%s%s/%s/%s.png" % (
                    OUTPUT_PATH,
                    d["site"],
                    d["type"],
                    str(date))
                # daily_plot(dfday, date, nvars, dest_file)
                dfr = dfday.resample("%ss" % d["interval"]).mean()
                daily_plot_avg(dfr, date, dest_file, d["site"], d["type"])
    else:  # specific device eg S1-bf
        df = encoder.get_df(site, origin)
        dflist = [group for group in df.groupby(df.index.date)]
        nvars = encoder.get_df_nvars(df)
        for date, dfday in dflist:
            dest_file = "%s%s/%s/%s.png" % (
                OUTPUT_PATH,
                site["site"],
                site["type"],
                str(date))
            # daily_plot(dfday, date, nvars, dest_file)
            dest_file = "%s%s/%s/%s/%s.png" % (
                OUTPUT_PATH,
                site["site"],
                site["type"],
                AVG_FOLDER,
                str(date))
            dfr = dfday.resample("%ss" % site["interval"]).mean()
            daily_plot_avg(dfr, date, dest_file, site["site"], site["type"])
            # discard values under MIN_DEPTH and MIN_TURB
            dfday = dfday[dfday["turbidity_00"] > MIN_TURB]
            dfday = dfday[dfday["depth_00"] > MIN_DEPTH]
            dfr = dfday.resample("%ss" % site["interval"]).mean()
            parts = dest_file.split('.')
            dest_file = ".".join(parts[:-1]) + '_clean' + '.' + parts[-1]
            daily_plot_avg(dfr, date, dest_file, site["site"], site["type"])


def daily_plot(df, date, nvars, dest_file):
    """ Plot all df vars in same figure """
    fig, axes = plt.subplots(ncols=1, nrows=len(nvars), sharex=True)
    df.plot(subplots=True, linewidth=0.25, ax=axes)
    for i, ax in enumerate(axes):
        ax.xaxis.set_major_locator(
            mdates.HourLocator(byhour=range(0, 24, 1)))
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M", tz=df.index.tz))
        ax.tick_params(axis="y", which="major", labelsize=10)
        ax.tick_params(axis="y", which="minor", labelsize=8)
        ax.tick_params(axis="x", which="major", labelsize=10)
        ax.tick_params(axis="x", which="minor", labelsize=8)
        # set name and units for each var/axes
        ax.set(xlabel="%s" % str(date), ylabel=nvars[i]["units"])
        ax.legend([nvars[i]["name"]])
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.savefig(
        dest_file,
        dpi=300)
    # free mem
    fig.clf()
    plt.close()
    del df
    gc.collect()


def daily_plot_avg(df, date, dest_file, site, instru):
    """ Plot Turb and Depth """
    print("Generating %s" % dest_file)
    nvars = ["turbidity_00", "depth_00"]
    df = df[nvars]  # just plot turb and depth
    fig, axes = plt.subplots(ncols=1, nrows=2, sharex=True)
    fig.suptitle("%s %s %s" % (site, instru, str(date)))
    df.plot(subplots=True, ax=axes, style=".")
    for i, ax in enumerate(axes):
        # sns.lineplot(data=df, x=df.index, y=df[nvars[i]], ax=ax)
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
        y_label = "%s (%s)" % (VARIABLES[nvars[i]]["name"],
                               VARIABLES[nvars[i]]["units"])
        ax.set(xlabel="%s" % str(date), ylabel=y_label)
        if i == 1:  # depth
            ax.axhline(0, ls="--", color="red")
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.savefig(
        dest_file,
        dpi=300)
    # free mem
    fig.clf()
    plt.close()
    del df
    gc.collect()


def plot_all_avg(origin="h5", site="all"):
    # Use seaborn style defaults and set the default figure size
    sns.set(rc={"figure.figsize": (24, 12)})
    dfaggr = None
    if site == "all":  # all instruments
        for d in DEVICES:
            dfr = site_avg_plot(
                origin=origin,
                device=d,
                plot_vars_x=PLOT_VARS["x"],
                plot_vars_y=PLOT_VARS["y"])
            if dfaggr is None:
                dfaggr = dfr
            else:
                dfaggr = dfaggr.append(dfr)
        # plot aggregate (all rows from all sites)
        site_avg_plot(
            df=dfaggr,
            plot_vars_x=PLOT_VARS["x"],
            plot_vars_y=PLOT_VARS["y"])
    else:  # specific device eg S1-bf
        site_avg_plot(
            origin=origin,
            device=site,
            plot_vars_x=PLOT_VARS["x"],
            plot_vars_y=PLOT_VARS["y"])


def site_avg_plot(origin=None, df=None, device=None,
                  plot_vars_x=[], plot_vars_y=[]):
    if device is None:  # aggregate
        print(df.shape)
        for s in ["Site", "Type"]:
            sns_plot = sns.pairplot(
                df,
                hue=s,
                height=8, aspect=1.5,
                plot_kws={
                    "s": 12,
                    "linewidth": 0.5,
                    "alpha": 0.6},
                x_vars=plot_vars_x,
                y_vars=plot_vars_y,
                dropna=True)
            sns_plot.fig.suptitle("All sites by %s" % s.lower())
            for i, v in enumerate(plot_vars_x):
                sns_plot.axes[1, i].set_xlabel("%s (%s)" % (
                    VARIABLES[v]["name"],
                    VARIABLES[v]["units"]))
            for i, v in enumerate(plot_vars_y):
                try:
                    sns_plot.axes[i, 0].set_ylabel("%s (%s)" % (
                        VARIABLES[v]["name"],
                        VARIABLES[v]["units"]))
                except KeyError:
                    sns_plot.axes[i, 0].set_ylabel("SD Turbidity (NTU)")
            dest_file = "%savg_by_%s.png" % (OUTPUT_PATH, s)
            sns_plot.savefig(dest_file, dpi=300)

            sns_plot = sns.lineplot(x=df.index.to_series(), y="turbidity_00",
                                    hue="Site", style="Type",
                                    data=df)
            sns_plot.set_title("Turbidity")

    else:  # device
        dest_file = "%s%s_%s.png" % (
                    OUTPUT_PATH,
                    device["site"],
                    device["type"])
        df = encoder.get_df(device, origin)
        # Resampling
        dfr = df.resample("%ss" % device["interval"]).mean()  # in seconds
        dfr["sd_turb"] = df.turbidity_00.resample("10min").std()
        print(dfr.shape)
        sns_plot = sns.pairplot(
            dfr,
            height=8, aspect=1.5,
            kind="reg",
            plot_kws={"line_kws": {"color": "red"}},
            x_vars=plot_vars_x,
            y_vars=plot_vars_y,
            dropna=True)
        sns_plot.fig.suptitle("%s %s" % (device["site"], device["type"]))
        for i, v in enumerate(plot_vars_x):
            sns_plot.axes[1, i].set_xlabel("%s (%s)" % (
                VARIABLES[v]["name"],
                VARIABLES[v]["units"]))
        for i, v in enumerate(plot_vars_y):
            try:
                sns_plot.axes[i, 0].set_ylabel("%s (%s)" % (
                    VARIABLES[v]["name"],
                    VARIABLES[v]["units"]))
            except KeyError:
                sns_plot.axes[i, 0].set_ylabel("SD Turbidity (NTU)")
        sns_plot.savefig(dest_file, dpi=300)
        # add to aggregate by device type seabed/floater
        dfr["Type"] = device["type"]
        dfr["Site"] = device["site"]
        return dfr


def plot_obs_calibration(origin):
    """ Plot all instr OBS calibration """
    sns.set(rc={"figure.figsize": (9, 8)})
    for t in INST_TYPES:
        devs = encoder.get_devices_by_type(t)
        fig, ax = plt.subplots()
        for d in devs:
            if len(d["T"]) > 0:
                ax.plot(d["T"], d["SSC"], label=d["site"], marker='o')
        xlabel = "%s (%s)" % (VARIABLES["turbidity_00"]["name"],
                              VARIABLES["turbidity_00"]["units"])
        ylabel = "%s (%s)" % (VARIABLES["ssc"]["name"],
                              VARIABLES["ssc"]["units"])
        ax.set(xlabel=xlabel, ylabel=ylabel)
        fig.legend(title='Sites', loc="center right")
        dest_file = "%sOBS_calib_%s.png" % (OUTPUT_PATH, t)
        fig.savefig(dest_file, dpi=200)
        # free mem
        fig.clf()
        plt.close()
        gc.collect()
