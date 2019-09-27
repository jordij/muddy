import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import scipy.io as sio
import seaborn as sns
import itertools
from constants import TIMEZONE, ADCP_DATES, EVENT_DATES, CALM_EVENT_DATES
from pandas.plotting import register_matplotlib_converters
from tools import station, encoder


register_matplotlib_converters()

FILEPATH = "./data/Currents/ADCP/"  # relative
INTERVAL = 1800


class Wave(object):
    VARS = [
        'WaterDepth',
        'Hs',
        'Tp',
        'Tm',
        'Dp',
        'Dp_TN'
    ]

    def __init__(self, site):
        """
        Wave data in two seprate files. Merge data into a single dataframe.
        """
        self.site = site

        folder_0 = "Site{0}/S{0}b_WaveStats_noQC.mat".format(
            site)
        datafile_0 = os.path.join(FILEPATH, folder_0)
        ml_data_0 = sio.loadmat(datafile_0)["WaveStats"]

        folder_1 = "Site{0}/S{0}a_WaveStats_noQC.mat".format(
            site)
        datafile_1 = os.path.join(FILEPATH, folder_1)
        ml_data_1 = sio.loadmat(datafile_1)["WaveStats"]

        # MATLAB datenum to Python
        timestamps = []
        timestamps.append(
            pd.to_datetime(ml_data_0["Time"][0][0][0][0]-719529, unit='D'))
        total_time = np.concatenate((ml_data_0["Time"][0][0],
                                    ml_data_1["Time"][0][0]))
        for i in range(1, len(total_time)):
            timestamps.append(timestamps[i-1] + pd.Timedelta("%ss" % INTERVAL))

        # Populate vars
        df_vars = {}
        for v in self.VARS:
            df_vars[v] = []

        for data in [ml_data_0, ml_data_1]:
            # bin vars
            for i in range(0, len(data["Hs"][0][0])):
                for v in self.VARS:
                    df_vars[v].append(data[v][0][0][i][0])
        df_vars["Time"] = timestamps
        df = pd.DataFrame.from_dict(df_vars)
        df = df.set_index("Time")
        df = df[ADCP_DATES["start"]:ADCP_DATES["end"]]
        df.index = df.index.tz_localize("UTC")
        df.index = df.index.tz_convert(TIMEZONE)
        self.df = df.replace(-1, np.NaN)
        self.concerto = encoder.create_device(
            "S%d" % self.site,
            "bedframe", "h5")

    def plot(self):
        concerto_df = self.concerto.df_avg
        weeks = self.df.index.week
        for week, df in self.df.groupby(weeks):
            cdf = concerto_df[
                    df.index.min():df.index.max()].resample('30Min').mean()
            fig, axes = plt.subplots(ncols=1, nrows=3,
                                     figsize=(28, 4))
            # water depth
            ax = axes[0]
            ax.plot(df.index, df["WaterDepth"], linestyle=":",
                    color="green", label="RDI water depth")
            ax.plot(cdf.index, cdf["depth_00"], linestyle=":",
                    color="blue", label="Concerto water depth")
            ax.set_ylabel("Water depth [m]")
            ax.set_ylim(bottom=0, top=max(
                df["WaterDepth"].max(),
                cdf["depth_00"].max()))
            # wave period
            ax = axes[1]
            ax.scatter(df.index, df["Tp"], s=5,
                       color="green", label="RDI wave period")
            ax.scatter(cdf.index, cdf["T"], s=5,
                       color="blue", label="Concerto wave period")
            ax.set_ylabel("Wave period [s]")
            # wave height
            ax = axes[2]
            ax.plot(df.index, df["Hs"],
                    color="green", label="Concerto Wave height")
            ax.plot(cdf.index, cdf["H"],
                    color="blue", label="RDI Wave height")
            ax.set_ylabel("Wave height [m]")
            fig.legend()

    def plot_interval(self, start=EVENT_DATES["start"], end=EVENT_DATES["end"]):
        """
        Plot interval defined by start/end dates
        """
        cdf = self.concerto.df_avg[start:end].resample('30Min').mean()
        df = self.df[start:end]

        fig, axes = plt.subplots(ncols=1, nrows=3,
                                     figsize=(28, 4))
        # water depth
        ax = axes[0]
        ax.plot(df.index, df["WaterDepth"], linestyle=":",
                color="green", label="RDI water depth")
        ax.plot(cdf.index, cdf["depth_00"], linestyle=":",
                color="blue", label="Concerto water depth")
        ax.set_ylabel("Water depth [m]")
        ax.set_ylim(bottom=0, top=max(
            df["WaterDepth"].max(),
            cdf["depth_00"].max()))
        # wave period
        ax = axes[1]
        ax.plot(df.index, df["Tp"],
                   color="green", label="RDI wave period")
        ax.plot(cdf.index, cdf["T"],
                   color="blue", label="Concerto wave period")
        ax.set_ylabel("Wave period [s]")
        # wave height
        ax = axes[2]
        ax.plot(df.index, df["Hs"],
                color="green", label="Concerto Wave height")
        ax.plot(cdf.index, cdf["H"],
                color="blue", label="RDI Wave height")
        ax.set_ylabel("Wave height [m]")
        fig.legend()
