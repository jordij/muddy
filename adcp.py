import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import scipy.io as sio
import seaborn as sns
import itertools
from constants import (TIMEZONE, AQUADOPPS_HEIGHTS, ADCP_DATES, DATES_FORMAT,
                       AQUADOPPS_SENS, AQUADOPPS_LEVELS)
from pandas.plotting import register_matplotlib_converters
from tools import station


register_matplotlib_converters()


FILEPATH = "D:/FoT_ADCP_data_09052019/Currents/ADCP/"
BINS = 40
INTERVAL = 600  # secs

VARS = ["a1", "a2", "a3",  # amplitudes
        "Vel_Mag", "Vel_Dir_TN",  # velocity mag. and dir
        "Vel_E_TN", "Vel_N_TN", "Vel_Up"]  # velocity components

SEN_HEADERS = [
    "Month",
    "Day",
    "Year",
    "Hour",
    "Minute",
    "Second",
    "Error code",
    "Status code",
    "Battery voltage",
    "Soundspeed",
    "Heading",
    "Pitch",
    "Roll",
    "Pressure",
    "Temperature",
    "Analog input 1",
    "Analog input 2"
]


class Adcp(object):
    """
    Represents an Aquadopp ADCP and its associated data
    """
    def __init__(self, site):
        self.site = site
        folder = "Site{0}/Processed/Currents_S{0}_noQC.mat".format(site)
        datafile = os.path.join(FILEPATH, folder)
        ml_data = sio.loadmat(datafile)
        # MATLAB datenum to Python
        timestamps = []
        timestamps.append(
            pd.to_datetime(ml_data["Time"][0][0]-719529, unit='D'))
        for i in range(1, len(ml_data["Time"])):
            timestamps.append(timestamps[i-1] + pd.Timedelta("%ss" % INTERVAL))
        # Populate vars
        df_vars = {}
        for v in VARS:
            df_vars[v] = []
        for i in range(0, len(ml_data["a1"])):
            for j in range(0, len(ml_data["a1"][i])):
                for v in VARS:
                    df_vars[v].append(ml_data[v][i][j])
        # Water depth
        wd = [m[0] for m in ml_data["WaterDepth"]]
        self.wd = pd.DataFrame(
            {"WaterDepth": wd},
            index=timestamps,
            columns=["WaterDepth"])
        self.wd = self.wd[ADCP_DATES["start"]:ADCP_DATES["end"]]
        self.wd.index.name = "Date"
        self.wd.index = self.wd.index.tz_localize(TIMEZONE)
        # Main dataframe
        index = list(itertools.product(timestamps, AQUADOPPS_HEIGHTS))
        indx = pd.MultiIndex.from_tuples(index, names=['Date', 'Height'])
        df = pd.DataFrame(df_vars, indx, VARS)
        df = df.tz_localize(TIMEZONE, level=0)
        df = df.loc[ADCP_DATES["start"]:ADCP_DATES["end"]]
        self.df = df.join(self.wd, how="left")
        self.df["OutOfWater"] = self.df.apply(
                lambda r: (r.WaterDepth - r.name[1]) <= 0.1,
                axis=1)
        # Sen file (temp, etc..)
        sen_folder = "Site{0}/{1}.sen".format(site, AQUADOPPS_SENS[site - 1])
        sen_datafile = os.path.join(FILEPATH, sen_folder)
        self.df_sen = pd.read_csv(sen_datafile, header=None, sep='\s+',
                                  parse_dates=[[0, 1, 2, 3, 4, 5]])
        self.df_sen.columns = ['date'] + SEN_HEADERS[-11:]
        self.df_sen['datetime'] = pd.to_datetime(self.df_sen['date'],
                                                 format='%m %d %Y %H %M %S')
        self.df_sen = self.df_sen.set_index("datetime")
        self.df_sen = self.df_sen[ADCP_DATES["start"]:ADCP_DATES["end"]]
        self.df_sen.index = self.df_sen.index.tz_localize(TIMEZONE)

    def __str__(self):
        return "Aquadopp %s" % self.site

    def unicode(self):
        return self.__str__()

    def plot_amplitude(self):
        for a in VARS[:3]:
            fig, axes = plt.subplots(ncols=1, nrows=4, figsize=(28, 4))
            cbar_ax = fig.add_axes([0.935, .108, .01, .75])
            cbar_ax.set_ylabel("Amplitude [counts]")
            i = 0
            weeks = self.df.index.get_level_values('Date').week
            for week, df in self.df.groupby(weeks):
                ax = axes[i]
                ax1 = ax.twinx()
                # Amplitude
                dfamp = df.reset_index().pivot(columns='Height', index='Date',
                                               values=a)
                # uncomment to show nans as 0
                # .fillna(0)
                sns.heatmap(
                    dfamp.transpose(), cmap='RdYlBu_r', vmin=0,
                    ax=ax, xticklabels=False, yticklabels=39,
                    linewidths=.0,
                    cbar=(i == 0),
                    cbar_ax=cbar_ax if i == 0 else None)
                ax.invert_yaxis()  # distance from bottom to top
                ax.set_ylabel("Distance above\nhead [m]")
                ax.set_ylim(bottom=0)
                ax.set_xlabel(None)
                # Water depth
                wd_df = self.wd[self.wd.index.week == week]
                wd_df.index = wd_df.index.strftime("%d-%m %H:%M")
                ax1.plot(wd_df.index, wd_df["WaterDepth"],
                         color="black", label="Water Depth [m]")
                ax1.set_ylabel("Water depth [m]")
                ax1.set_ylim(bottom=0, top=self.wd["WaterDepth"].max())
                ax1.xaxis.set_ticks(
                    np.arange(72, wd_df.WaterDepth.count() + 1, 72))
                ax1.set_xlabel(None)
                i += 1
            fig.suptitle("%s - %s" % (str(self), a))

    def plot_velocity(self):
        for v in VARS[-3:]:
            fig, axes = plt.subplots(ncols=1, nrows=4, figsize=(28, 4))
            cbar_ax = fig.add_axes([0.935, .108, .01, .75])
            cbar_ax.set_ylabel("Velocity [m/s]")
            i = 0
            weeks = self.df.index.get_level_values('Date').week
            for week, df in self.df.groupby(weeks):
                ax = axes[i]
                ax1 = ax.twinx()
                # Velocity
                dfamp = df.reset_index().pivot(columns='Height', index='Date',
                                               values=v)
                # uncomment to show nans as 0
                # .fillna(0)
                sns.heatmap(
                    dfamp.transpose(), cmap='RdYlBu_r',
                    ax=ax, xticklabels=False, yticklabels=39,
                    linewidths=.0,
                    cbar=(i == 0),
                    cbar_ax=cbar_ax if i == 0 else None)
                ax.invert_yaxis()  # distance from bottom to top
                ax.set_ylabel("Distance above\nhead [m]")
                ax.set_ylim(bottom=0)
                ax.set_xlabel(None)
                # Water depth
                wd_df = self.wd[self.wd.index.week == week]
                wd_df.index = wd_df.index.strftime("%d-%m %H:%M")
                ax1.plot(wd_df.index, wd_df["WaterDepth"],
                         color="black", label="Water Depth [m]")
                ax1.set_ylabel("Water depth [m]")
                ax1.set_ylim(bottom=0, top=self.wd["WaterDepth"].max())
                ax1.xaxis.set_ticks(
                    np.arange(72, wd_df.WaterDepth.count() + 1, 72))
                ax1.set_xlabel(None)
                i += 1
            fig.suptitle("%s - %s" % (str(self), v))

    def plot_magnitude(self):
        dfwindlist = station.get_weekly_wind()
        weeks = self.df.index.get_level_values('Date').week
        i = 0
        for week, df in self.df.groupby(weeks):
            dfwind = dfwindlist[i]
            fig, axes = plt.subplots(ncols=1, nrows=4, figsize=(28, 4), sharex=True)
            ax = axes[0]
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
            # Temperature
            ax = axes[1]
            df_sen = self.df_sen[self.df_sen.index.week == week]
            ax.plot(df_sen.index, df_sen["Temperature"])
            ax.set_ylabel("Temperature [°C]")
            # Velocity magnitude & direction
            ax = axes[2]
            ax1 = axes[3]
            levels = AQUADOPPS_LEVELS[self.site - 1]
            subdf = df.loc[pd.IndexSlice[:, levels[0]], :]
            subdf.index = subdf.index.droplevel(level=1)  # drop height
            ax.plot(subdf.index, subdf["Vel_Mag"],
                    color="blue", label='%.1f mab' % levels[0])
            ax1.scatter(subdf.index, subdf["Vel_Dir_TN"],
                        color="blue", label='%.1f mab' % levels[0], s=3)
            subdf = df.loc[pd.IndexSlice[:, levels[1]], :]
            subdf.index = subdf.index.droplevel(level=1)  # drop height
            ax.plot(subdf.index, subdf["Vel_Mag"],
                    color="red", label='%.1f mab' % levels[1])
            ax1.scatter(subdf.index, subdf["Vel_Dir_TN"],
                        color="red", label='%.1f mab' % levels[1], s=3)
            subdf = df.loc[pd.IndexSlice[:, levels[2]], :]
            subdf.index = subdf.index.droplevel(level=1)  # drop height
            ax.plot(subdf.index, subdf["Vel_Mag"],
                    color="green", label='%.1f mab' % levels[2])
            ax1.scatter(subdf.index, subdf["Vel_Dir_TN"],
                        color="green", label='%.1f mab' % levels[2], s=3)
            ax.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax1.legend(loc="center left", bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax.set_ylabel("Velocity\nspeed [m/s]")
            ax1.set_ylabel("Velocity\ndir. [°C]")
            fig.suptitle("%s - Week %s" % (str(self), i + 1))
            i += 1
