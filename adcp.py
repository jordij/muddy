import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import scipy.io as sio
import seaborn as sns
import itertools
from constants import TIMEZONE, AQUADOPPS_HEIGHTS, ADCP_DATES, DATES_FORMAT
from pandas.plotting import register_matplotlib_converters


register_matplotlib_converters()


FILEPATH = "D:/FoT_ADCP_data_09052019/Currents/ADCP/"
BINS = 40
INTERVAL = 600  # secs

VARS = ["a1", "a2", "a3", "Vel_E_TN", "Vel_Dir_TN", "Vel_Up"]


class Adcp(object):
    """
    Represents an Aquadopp ADCP and its associated data
    """
    def __init__(self, site):
        self.site = site
        folder = "Site{0}/Processed/Currents_S{0}_noQC.mat".format(site)
        self.datafile = os.path.join(FILEPATH, folder)
        ml_data = sio.loadmat(self.datafile)
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

        wd = [m[0] for m in ml_data["WaterDepth"]]
        self.wd = pd.DataFrame(
            {"WaterDepth": wd},
            index=timestamps,
            columns=["WaterDepth"])
        self.wd = self.wd[ADCP_DATES["start"]:ADCP_DATES["end"]]
        self.wd.index.name = "Date"
        index = list(itertools.product(timestamps, AQUADOPPS_HEIGHTS))
        indx = pd.MultiIndex.from_tuples(index, names=['Date', 'Height'])
        df = pd.DataFrame(df_vars, indx, VARS)
        df = df.loc[ADCP_DATES["start"]:ADCP_DATES["end"]]
        self.df = df.join(self.wd, how="left")
        self.df["OutOfWater"] = self.df.apply(
                lambda r: (r.WaterDepth - r.name[1]) <= 0.1,
                axis=1)
        self.ml_data = ml_data
        # self.df["WaterDepth"] = np.nan
        # for d in self.df.index.get_level_values('Date'):
        #     # for h in self.df.index.get_level_values('Height'):
        #     self.df.loc[d, :]["WaterDepth"] = self.wd.loc[d]["WaterDepth"]

        # self.df = pd.DataFrame(data_dict)
        # self.df = self.df.set_index("time")
        # self.df.index = self.df.index.tz_localize(TIMEZONE)

    def __str__(self):
        return "Aquadopp %s" % self.site

    def unicode(self):
        return self.__str__()

    def plot_amplitude(self):
        for a in VARS[:3]:
            fig, axes = plt.subplots(ncols=1, nrows=4, figsize=(28, 4))
            cbar_ax = fig.add_axes([0.925, .108, .01, .8])
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
                # dfamp.index = dfamp.index.strftime('%d-%m')
                sns.heatmap(
                    dfamp.transpose(), cmap='RdYlBu_r', vmin=0,
                    ax=ax, xticklabels=False, yticklabels=39,
                    linewidths=.0,
                    cbar=(i == 0),
                    cbar_ax=cbar_ax if i == 0 else None)
                ax.invert_yaxis()  # distance from bottom to top
                ax.set_ylabel("Distance above\nhead [m]")
                ax.set_ylim(bottom=0)
                # Water depth
                wd_df = self.wd[self.wd.index.week == week]
                wd_df.index = wd_df.index.strftime("%d-%m %H:%M")
                ax1.plot(wd_df.index, wd_df["WaterDepth"], color="black", label="Water Depth [m]")
                ax1.set_ylabel("Water depth [m]")
                ax1.set_ylim(bottom=0, top=self.wd["WaterDepth"].max())
                ax1.xaxis.set_ticks(np.arange(72, wd_df.WaterDepth.count() + 1, 72))
                i += 1
            fig.suptitle("%s - %s" % (str(self), a))
