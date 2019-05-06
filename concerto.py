# -*- coding: utf-8 -*-
"""
Daily plots for raw data in .rsk files.
@author: @jordij
"""
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyrsktools
import seaborn as sns

rawpath = "D:/EE-FoT-May2017Expt/Concertos/RawData/"
devices = [
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
s1floater = "data/concertos/S1_Floater_066010_20170704_0850.rsk"
temperatures = [
    ["temperature_00", "Temperature"], 
    ["pressuretemperature_00", "Pressure temperature"],
    ["conductivitycelltemperature_00", "Conductivity cell temperature"]
]
conductivity = ["conductivity_00", "Conductivity", "mS/cm"]
pressure = ["pressure_00", "Pressure", "dbar"]
turbidity = ["turbidity_00", "Turbidity", "NTU"]
# Use seaborn style defaults and set the default figure size
sns.set(rc={'figure.figsize':(11, 4)})


for device in devices:
    datapath = "%s%s" % (rawpath, device['file'])
    with pyrsktools.open(datapath) as rsk:
        # Pandas dataframe for the win
        df = pd.DataFrame(rsk.npsamples())
        # timestamp as index, then UTC to NZ
        df = df.set_index("timestamp")
        df.index = df.index.tz_convert('Pacific/Auckland')
        df_min = int(math.floor(min(df.temperature_00))) - 1
        df_max = int(math.ceil(max(df.temperature_00))) + 1
        # group data by day, month, year (unique day)
        # returns tuple (date, dataframe)
        dflist = [group for group in df.groupby(df.index.date)]
        for variable in [conductivity, turbidity, pressure]:
            if variable[0] in df.columns:
                print("%s for %s - %s \n" % (variable[1], device['name'], device['type']))
            else:
                print("%s NOT available for %s - %s \n" % (conductivity[1], device['name'], device['type']))
        for temp in temperatures:
            if temp[0] in df.columns:
                print("%s for %s - %s \n" % (temp[1], device['name'], device['type']))
            else:
                print("%s NOT available for %s - %s \n" % (temp[1], device['name'], device['type']))
        
        for dfday_date, dfday in dflist:

            # TEMPERATURES
            for temp in temperatures:
                if temp[0] in df.columns:
                    fig, ax = plt.subplots()
                    ax.plot(dfday.index, dfday[temp[0]], linewidth=0.5)
                    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 1)))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                    ax.tick_params(axis='y', which='major', labelsize=6)
                    ax.tick_params(axis='y', which='minor', labelsize=4)
                    ax.tick_params(axis='x', which='major', labelsize=6)
                    ax.tick_params(axis='x', which='minor', labelsize=4)
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
                                device['name'],
                                device['type'],
                                temp[0],
                                str(dfday_date)),
                        dpi=200)
                    plt.close()
            
            # CONDUCTIVITY
            if conductivity[0] in df.columns:
                fig, ax = plt.subplots()
                ax.plot(dfday.index, dfday[conductivity[0]], linewidth=0.5)
                ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 1)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                ax.tick_params(axis='y', which='major', labelsize=6)
                ax.tick_params(axis='y', which='minor', labelsize=4)
                ax.tick_params(axis='x', which='major', labelsize=6)
                ax.tick_params(axis='x', which='minor', labelsize=4)
                ax.set(
                    xlabel="Time",
                    ylabel=conductivity[2],
                    title='%s %s' % (str(dfday_date), conductivity[1]))
                ax.margins(x=0.01)
                fig.autofmt_xdate()
                fig.tight_layout()
                plt.savefig(
                    "./output/%s/%s/%s/%s_raw.png" % (
                            device['name'],
                            device['type'],
                            conductivity[0],
                            str(dfday_date)),
                    dpi=200)
                plt.close()
            
            # TURBIDITY
            if turbidity[0] in df.columns:
                fig, ax = plt.subplots()
                ax.plot(dfday.index, dfday[turbidity[0]], linewidth=0.5)
                ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 1)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                ax.tick_params(axis='y', which='major', labelsize=6)
                ax.tick_params(axis='y', which='minor', labelsize=4)
                ax.tick_params(axis='x', which='major', labelsize=6)
                ax.tick_params(axis='x', which='minor', labelsize=4)
                ax.set(
                    xlabel="Time",
                    ylabel=turbidity[2],
                    title='%s %s' % (str(dfday_date), turbidity[1]))
                ax.margins(x=0.01)
                fig.autofmt_xdate()
                fig.tight_layout()
                plt.savefig(
                    "./output/%s/%s/%s/%s_raw.png" % (
                            device['name'],
                            device['type'],
                            turbidity[0],
                            str(dfday_date)),
                    dpi=200)
                plt.close()
            
            # PRESSURE
            if pressure[0] in df.columns:
                fig, ax = plt.subplots()
                ax.plot(dfday.index, dfday[pressure[0]], linewidth=0.5)
                ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 1)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=dfday.index.tz))
                ax.tick_params(axis='y', which='major', labelsize=6)
                ax.tick_params(axis='y', which='minor', labelsize=4)
                ax.tick_params(axis='x', which='major', labelsize=6)
                ax.tick_params(axis='x', which='minor', labelsize=4)
                ax.set(
                    xlabel="Time",
                    ylabel=pressure[2],
                    title='%s %s' % (str(dfday_date), pressure[1]))
                ax.margins(x=0.01)
                fig.autofmt_xdate()
                fig.tight_layout()
                plt.savefig(
                    "./output/%s/%s/%s/%s_raw.png" % (
                            device['name'],
                            device['type'],
                            pressure[0],
                            str(dfday_date)),
                    dpi=200)
                plt.close()
                
            
