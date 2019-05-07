# -*- coding: utf-8 -*-
"""
Daily plots for raw data in .rsk files.
@author: @jordij
"""
import gc
import fire
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyrsktools
import seaborn as sns
import tabulate

RAWPATH = "D:/EE-FoT-May2017Expt/Concertos/RawData/"
OBS_VARS = [
    ["conductivity_00", "mS/cm", "Conductivity"],
    ["temperature_00", "°C", "Temperature"],
    ["pressure_00", "dbar", "Pressure"],
    ["turbidity_00", "NTU", "Turbidity"],
    ["pressuretemperature_00", "°C", "Pressure temperature"],
    ["conductivitycelltemperature_00", "°C", "Conductivity cell temperature"]
]
DEVICES = [
    {"name": "S1", "file": "066010_20170704_0850.rsk", "type": "floater"},
    {"name": "S2", "file": "065761_20170702_1030.rsk", "type": "floater"},
    {"name": "S4", "file": "065762_20170630_1524.rsk", "type": "floater"},
    {"name": "S5", "file": "065760_20170702_1005.rsk", "type": "floater"},
    {"name": "S1", "file": "066011_20170703_1431.rsk", "type": "bedframe"},
    {"name": "S2", "file": "065818_20170701_0947.rsk", "type": "bedframe"},
    {"name": "S3", "file": "065819_20170701_0953.rsk", "type": "bedframe"},
    {"name": "S4", "file": "065821_20170703_1419.rsk", "type": "bedframe"},
    {"name": "S5", "file": "065820_20170704_0838.rsk", "type": "bedframe"}
]

TEMPS = [
    ["temperature_00", "Temperature"],
    ["pressuretemperature_00", "Pressure temperature"],
    ["conductivitycelltemperature_00", "Conductivity cell temperature"]
]
CONDUC = ["conductivity_00", "Conductivity", "mS/cm"]
PRESS = ["pressure_00", "Pressure", "dbar"]
TURBID = ["turbidity_00", "Turbidity", "NTU"]


def devicesTable(dataframe, index):
    nvars = 0
    for v in [CONDUC, TURBID, PRESS]:
        if v[0] in dataframe.columns:
            DEVICES[index][v[1]] = "Yes"
            nvars = nvars + 1
        else:
            DEVICES[v[1]] = "No"
    for temp in TEMPS:
        if temp[0] in dataframe.columns:
            DEVICES[index][temp[1]] = "Yes"
            nvars = nvars + 1
        else:
            DEVICES[index][temp[1]] = "No"
    return nvars


def generate(plot_all=True):
    # Use seaborn style defaults and set the default figure size
    if plot_all:
        sns.set(rc={'figure.figsize': (12, 12)})
    else:
        sns.set(rc={'figure.figsize': (11, 4)})
    mainidx = 0
    for d in DEVICES:
        datapath = "%s%s" % (RAWPATH, d['file'])
        with pyrsktools.open(datapath) as rsk:
            # Pandas dataframe for the win
            df = pd.DataFrame(rsk.npsamples())
            # timestamp as index, then UTC to NZ
            df = df.set_index("timestamp")
            df.index = df.index.tz_convert('Pacific/Auckland')
            # group data by day, month, year (unique day)
            # returns tuple (date, dataframe)
            dflist = [group for group in df.groupby(df.index.date)]
            nvars = devicesTable(df, mainidx)
            for dfday_date, dfday in dflist:
                if plot_all:  # plot all vars in the same figure
                    fig, axes = plt.subplots(ncols=1, nrows=nvars, sharex=True)
                    dfday.plot(subplots=True, linewidth=0.25, ax=axes)
                    idx = 0
                    for ax in axes:
                        ax.xaxis.set_major_locator(
                            mdates.HourLocator(byhour=range(0, 24, 1)))
                        ax.xaxis.set_major_formatter(
                            mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                        ax.tick_params(axis='y', which='major', labelsize=10)
                        ax.tick_params(axis='y', which='minor', labelsize=8)
                        ax.tick_params(axis='x', which='major', labelsize=10)
                        ax.tick_params(axis='x', which='minor', labelsize=8)
                        ax.set(xlabel='Time', ylabel=OBS_VARS[idx][1])
                        ax.legend([OBS_VARS[idx][2]])
                        idx += 1
                    fig.autofmt_xdate()
                    fig.tight_layout()
                    plt.savefig(
                        "./output/%s/%s/all/%s_raw.png" % (
                            d['name'],
                            d['type'],
                            str(dfday_date)),
                        dpi=300)
                    fig.clf()
                    plt.close()
                    del dfday
                    gc.collect()
                else:  # plot each variable separately
                    fig, axes = plt.subplots(ncols=1, nrows=nvars, sharex=True)
                    dfday.plot(subplots=True, linewidth=0.25, ax=axes)
                    idx = 0
                    for ax in axes:
                        ax.xaxis.set_major_locator(
                            mdates.HourLocator(byhour=range(0, 24, 1)))
                        ax.xaxis.set_major_formatter(
                            mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                        ax.tick_params(axis='y', which='major', labelsize=10)
                        ax.tick_params(axis='y', which='minor', labelsize=8)
                        ax.tick_params(axis='x', which='major', labelsize=10)
                        ax.tick_params(axis='x', which='minor', labelsize=8)
                        ax.set(xlabel='Time', ylabel=OBS_VARS[idx][1])
                        ax.legend([OBS_VARS[idx][2]])
                        idx += 1
                    fig.autofmt_xdate()
                    fig.tight_layout()
                    plt.savefig(
                        "./output/%s/%s/%s_raw.png" % (
                            d['name'],
                            d['type'],
                            str(dfday_date)),
                        dpi=300)
                    plt.close()
                    # TEMPERATURES
                    for temp in TEMPS:
                        if temp[0] in df.columns:
                            fig, ax = plt.subplots()
                            ax.plot(dfday.index, dfday[temp[0]], linewidth=0.5)
                            ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 1)))
                            ax.xaxis.set_major_formatter(
                                mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                            ax.tick_params(
                                axis='y', which='major', labelsize=6)
                            ax.tick_params(
                                axis='y', which='minor', labelsize=4)
                            ax.tick_params(
                                axis='x', which='major', labelsize=6)
                            ax.tick_params(
                                axis='x', which='minor', labelsize=4)
                            ax.set(
                                xlabel='Time',
                                ylabel='°C',
                                title='%s %s' % (str(dfday_date), temp[1]))
                            ax.yaxis.set_ticks(np.arange(-5, 30, 5))
                            ax.margins(x=0.01)
                            fig.autofmt_xdate()
                            fig.tight_layout()
                            plt.savefig(
                                "./output/%s/%s/%s/%s_raw.png" % (
                                    d['name'],
                                    d['type'],
                                    temp[0],
                                    str(dfday_date)),
                                dpi=200)
                            plt.close()

                    # CONDUCTIVITY
                    if CONDUC[0] in df.columns:
                        fig, ax = plt.subplots()
                        ax.plot(
                            dfday.index, dfday[CONDUC[0]], linewidth=0.5)
                        ax.xaxis.set_major_locator(
                            mdates.HourLocator(byhour=range(0, 24, 1)))
                        ax.xaxis.set_major_formatter(
                            mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                        ax.tick_params(axis='y', which='major', labelsize=6)
                        ax.tick_params(axis='y', which='minor', labelsize=4)
                        ax.tick_params(axis='x', which='major', labelsize=6)
                        ax.tick_params(axis='x', which='minor', labelsize=4)
                        ax.set(
                            xlabel="Time",
                            ylabel=CONDUC[2],
                            title='%s %s' % (str(dfday_date), CONDUC[1]))
                        ax.margins(x=0.01)
                        fig.autofmt_xdate()
                        fig.tight_layout()
                        plt.savefig(
                            "./output/%s/%s/%s/%s_raw.png" % (
                                d['name'],
                                d['type'],
                                CONDUC[0],
                                str(dfday_date)),
                            dpi=200)
                        plt.close()

                    # TURBIDITY
                    if TURBID[0] in df.columns:
                        fig, ax = plt.subplots()
                        ax.plot(
                            dfday.index, dfday[TURBID[0]], linewidth=0.5)
                        ax.xaxis.set_major_locator(
                            mdates.HourLocator(byhour=range(0, 24, 1)))
                        ax.xaxis.set_major_formatter(
                            mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                        ax.tick_params(axis='y', which='major', labelsize=6)
                        ax.tick_params(axis='y', which='minor', labelsize=4)
                        ax.tick_params(axis='x', which='major', labelsize=6)
                        ax.tick_params(axis='x', which='minor', labelsize=4)
                        ax.set(
                            xlabel="Time",
                            ylabel=TURBID[2],
                            title='%s %s' % (str(dfday_date), TURBID[1]))
                        ax.margins(x=0.01)
                        fig.autofmt_xdate()
                        fig.tight_layout()
                        plt.savefig(
                            "./output/%s/%s/%s/%s_raw.png" % (
                                d['name'],
                                d['type'],
                                TURBID[0],
                                str(dfday_date)),
                            dpi=200)
                        plt.close()

                    # PRESSURE
                    if PRESS[0] in df.columns:
                        fig, ax = plt.subplots()
                        ax.plot(dfday.index, dfday[PRESS[0]], linewidth=0.5)
                        ax.xaxis.set_major_locator(
                            mdates.HourLocator(byhour=range(0, 24, 1)))
                        ax.xaxis.set_major_formatter(
                            mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                        ax.tick_params(axis='y', which='major', labelsize=6)
                        ax.tick_params(axis='y', which='minor', labelsize=4)
                        ax.tick_params(axis='x', which='major', labelsize=6)
                        ax.tick_params(axis='x', which='minor', labelsize=4)
                        ax.set(
                            xlabel="Time",
                            ylabel=PRESS[2],
                            title='%s %s' % (str(dfday_date), PRESS[1]))
                        ax.margins(x=0.01)
                        fig.autofmt_xdate()
                        fig.tight_layout()
                        plt.savefig(
                            "./output/%s/%s/%s/%s_raw.png" % (
                                d['name'],
                                d['type'],
                                PRESS[0],
                                str(dfday_date)),
                            dpi=200)
                        plt.close()
    # print clean table of sites vs available variables
    header = DEVICES[0].keys()
    rows = [x.values() for x in DEVICES]
    print(tabulate.tabulate(rows, header))


if __name__ == '__main__':
    fire.Fire(generate)
