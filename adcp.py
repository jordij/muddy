import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import scipy.io as sio
import seaborn as sns
import itertools
from constants import TIMEZONE, ADCP_DATES
from pandas.plotting import register_matplotlib_converters
from tools import station


register_matplotlib_converters()


FILEPATH = "./data/Currents/ADCP/"  # relative

INTERVAL = 600  # secs

AQUADOPPS_SENS = ["A243401", "EXTIKI02", "HR02"]
ADCP_LEVELS = [  # levels per site
    [0.3, 0.5, 0.7],
    [0.3, 0.6, 1.1],
    [0.3, 1, 2],
    [np.float32(0.6), np.float32(1.4), np.float32(2.6)],
    [1.27, 3.02, 4.52],
]
ADCP_A1_LEVELS = [  # anything with a1 lower than these values is removed
    80,
    None,
    60,
    55
]


class ADCP(object):
    VARS = []
    WD = "WaterDepth"
    AMPLITUDES = []
    HEIGHTS = []

    def __str__(self):
        return "RDI %s" % self.site

    def unicode(self):
        return self.__str__()

    def __init__(self, site):
        """ Method to be implemented in each subclass """
        raise NotImplementedError("Must load data into dataframe")

    def plot_amplitude(self):
        for a in self.AMPLITUDES:
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
                    ax=ax, xticklabels=False, yticklabels=len(self.HEIGHTS)-1,
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
                ax1.plot(wd_df.index, wd_df[self.WD],
                         color="black", label="Water Depth [m]")
                ax1.set_ylabel("Water depth [m]")
                ax1.set_ylim(bottom=0, top=self.wd[self.WD].max())
                ax1.xaxis.set_ticks(
                    np.arange(72, wd_df.WaterDepth.count() + 1, 72))
                ax1.set_xlabel(None)
                i += 1
            fig.suptitle("%s - %s" % (str(self), a))


class RDI(ADCP):
    VARS = [
        'SerEA1cnt', 'SerEA2cnt', 'SerEA3cnt', 'SerEA4cnt',
        'SerC1cnt', 'SerC2cnt', 'SerC3cnt', 'SerC4cnt',
        'SerPG1', 'SerPG2', 'SerPG3', 'SerPG4',
        'Vel_E_TN', 'Vel_N_TN', 'Vel_Mag', 'Vel_Dir_TN', 'Vel_Up'
    ]
    AMPLITUDES = ['SerEA1cnt', 'SerEA2cnt', 'SerEA3cnt', 'SerEA4cnt']
    HEIGHTS = np.arange(1.27, 10.27, 0.25, dtype=np.float32)

    def __init__(self, site):
        """
        RDI in two seprate files. Merge data into a single dataframe.
        """
        self.site = site

        folder_0 = "Site{0}/Currents_Site{0}_Filepart{1}_noQC.mat".format(
            site, 2)
        datafile_0 = os.path.join(FILEPATH, folder_0)
        ml_data_0 = sio.loadmat(datafile_0)

        folder_1 = "Site{0}/Currents_Site{0}_Filepart{1}_noQC.mat".format(
            site, 1)
        datafile_1 = os.path.join(FILEPATH, folder_1)
        ml_data_1 = sio.loadmat(datafile_1)

        # MATLAB datenum to Python
        timestamps = []
        timestamps.append(
            pd.to_datetime(ml_data_0["Time"][0][0]-719529, unit='D'))
        # round to 00.00 secs
        timestamps[0] = timestamps[0] - pd.Timedelta(
            microseconds=timestamps[0].microsecond)
        timestamps[0] = timestamps[0] - pd.Timedelta(
            nanoseconds=timestamps[0].nanosecond)
        total_time = np.concatenate((ml_data_0["Time"], ml_data_1["Time"]))
        for i in range(1, len(total_time)):
            timestamps.append(timestamps[i-1] + pd.Timedelta("%ss" % INTERVAL))

        # Populate vars
        df_vars = {}
        for v in self.VARS:
            df_vars[v] = []

        wd = []
        for data in [ml_data_0, ml_data_1]:
            # bin vars
            for i in range(0, len(data["Vel_E_TN"])):
                for j in range(0, len(data["Vel_E_TN"][i])):
                    for v in self.VARS:
                        df_vars[v].append(data[v][i][j])
                # water depth
                wd.append(data[self.WD][i][0])
        wd = pd.DataFrame(
            {self.WD: wd},
            index=timestamps,
            columns=[self.WD])
        wd = wd[ADCP_DATES["start"]:ADCP_DATES["end"]]
        wd.index.name = "Date"
        wd.index = wd.index.tz_localize(TIMEZONE)
        self.wd = wd

        # Main dataframe
        index = list(itertools.product(timestamps, self.HEIGHTS))
        indx = pd.MultiIndex.from_tuples(index, names=['Date', 'Height'])
        df = pd.DataFrame(df_vars, indx, self.VARS)
        df = df.tz_localize(TIMEZONE, level=0)
        df = df.loc[ADCP_DATES["start"]:ADCP_DATES["end"]]
        self.df = df.join(wd, how="left")

    def plot_magnitude(self):
        dfwindlist = station.get_weekly_wind()
        weeks = self.df.index.get_level_values('Date').week
        i = 0
        for week, df in self.df.groupby(weeks):
            dfwind = dfwindlist[i]
            fig, axes = plt.subplots(ncols=1, nrows=4,
                                     figsize=(28, 4), sharex=True)
            ax = axes[0]
            ax.scatter(dfwind.index, dfwind["speed"], s=4, c="black",
                       label="Wind speed\n[m/s]")
            ax.set_ylabel("Wind speed\n[m/s]")
            ax.set_yticks([0, 7, 14])
            ax.spines["left"].set_bounds(0, 14)
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax = ax.twinx()
            ax.scatter(dfwind.index, dfwind["direction"],
                       marker="x", label="Wind direction\n[degrees]")
            ax.set_ylabel("Wind direction\n[degrees]")
            ax.set_yticks([0, 90, 180, 270, 360])
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.35), frameon=False)
            ax.spines["right"].set_bounds(0, 360)
            ax.xaxis.set_visible(False)
            ax.spines["right"].set_position(("outward", 15))
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)
            # Water depth
            ax = axes[1]
            df_sen = self.wd[self.wd.index.week == week]
            ax.plot(df_sen.index, df_sen["WaterDepth"], linestyle=":",
                    color="black", label="Water Depth [m]")
            ax.set_ylabel("Water depth [m]")
            ax.set_ylim(bottom=0, top=self.wd["WaterDepth"].max())
            # Velocity magnitude & direction
            ax = axes[2]
            ax1 = axes[3]
            levels = ADCP_LEVELS[self.site - 1]
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
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax1.legend(loc="center left",
                       bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax.set_ylabel("Velocity\nspeed [m/s]")
            ax1.set_ylabel("Velocity\ndir. [°C]")
            fig.suptitle("%s - Week %s" % (str(self), i + 1))
            i += 1

    def __str__(self):
        return "RDI %s" % self.site


class Signature1000(ADCP):
    """
    Represents an Signature1000 ADCP and its associated data
    """
    VARS = [
        # 'Burst_Velocity_ENU',
        'Burst_Amplitude_Beam',
        # 'Burst_Correlation_Beam',
        'IBurst_Velocity_Beam',
        'IBurst_Amplitude_Beam',
        'IBurst_Correlation_Beam',
        # 'Burst_Pressure',
        # 'Burst_Heading',
        # 'Burst_Roll',
        # 'Burst_Temperature',
        'Vel_E_TN',
        'Vel_N_TN',
        'Vel_Mag',
        'Vel_Dir_TN',
        # 'Burst_Pitch'
    ]

    IND_VARS = [
        'Burst_Heading',
        'Burst_Pressure',
        'Burst_Temperature',
    ]

    AMPLITUDES = ['a1', 'a2', 'a3', 'a4']
    HEIGHTS = np.arange(0.6, 8.2, 0.2, dtype=np.float32)

    def __init__(self, site):
        folder = "Site{0}/FoT_Signature1000_S{0}_BurstStats_noQC.mat".format(
            site)
        datafile = os.path.join(FILEPATH, folder)
        ml_data = sio.loadmat(datafile)["BurstStats"]
        self.site = site
        # MATLAB datenum to Python
        timestamps = []
        timestamps.append(
            pd.to_datetime(ml_data["Time"][0][0][0][0]-719529, unit='D'))
        # round to 00.00 secs
        timestamps[0] = timestamps[0] - pd.Timedelta(
            microseconds=timestamps[0].microsecond)
        timestamps[0] = timestamps[0] - pd.Timedelta(
            nanoseconds=timestamps[0].nanosecond)
        for i in range(1, len(ml_data["Time"][0][0])):
            timestamps.append(timestamps[i-1] + pd.Timedelta("%ss" % INTERVAL))
        # Populate vars
        df_vars = {}
        for v in self.VARS:
            df_vars[v] = []
        for i in range(0, len(ml_data["Vel_E_TN"][0][0])):
            for j in range(0, len(ml_data["Vel_E_TN"][0][0][i])):
                for v in self.VARS:
                    df_vars[v].append(ml_data[v][0][0][i][j])
        # Water depth
        wd = [m[0] for m in ml_data["Burst_Pressure"][0][0]]
        wt = [m[0] for m in ml_data["Burst_Temperature"][0][0]]
        wd = pd.DataFrame(
            {"WaterDepth": wd, 'Temperature': wt},
            index=timestamps,
            columns=["WaterDepth", "Temperature"])
        wd = wd[ADCP_DATES["start"]:ADCP_DATES["end"]]
        wd.index.name = "Date"
        wd.index = wd.index.tz_localize(TIMEZONE)
        self.wd = wd
        # Main dataframe
        index = list(itertools.product(timestamps, self.HEIGHTS))
        indx = pd.MultiIndex.from_tuples(index, names=['Date', 'Height'])
        df = pd.DataFrame(df_vars, indx, self.VARS)
        df = df.tz_localize(TIMEZONE, level=0)
        df[self.AMPLITUDES] = pd.DataFrame(
            df.Burst_Amplitude_Beam.values.tolist(), index=df.index)
        df = df.drop(columns="Burst_Amplitude_Beam")
        df = df.loc[ADCP_DATES["start"]:ADCP_DATES["end"]]
        self.df = df.join(self.wd, how="left")
        # clean data
        if ADCP_A1_LEVELS[self.site - 1] is not None:
            vars_nan = self.VARS[-(len(self.VARS)-1):] + self.AMPLITUDES
            self.df.loc[self.df.a1 < ADCP_A1_LEVELS[self.site - 1],
                        vars_nan] = np.NaN
            # self.df["OutOfWater"] = self.df.apply(
            #     lambda r: r.IBurst_Correlation_Beam < 70,
            #     axis=1)
            # self.df.loc[self.df.OutOfWater, vars_nan] = np.NaN
            # self.df["minHeight"] = self.df.apply(
            #     lambda r: self.df.loc[
            #         r.name[0], ].query("OutOfWater == True").index.min(),
            #     axis=1)
            # too expensive, not good to iterate on DF and perform updates..
            # for i in self.df.index.get_level_values(0):
            #     for j in self.df.loc[i].index.get_level_values(0):
            #         if self.df.loc[i, j].OutOfWater:
            #             lower_idx = list(filter(lambda x: x > j,
            #                              self.HEIGHTS))
            #             self.df.loc[(i, lower_idx), vars_nan] = np.NaN

    def clean_by_hah(self, threshold=1, min_hah=0.8):
        # agressive cleanup
        vars_nan = self.VARS[-(len(self.VARS)-1):] + self.AMPLITUDES
        lower_idx = list(filter(lambda x: x > min_hah,
                                self.HEIGHTS))
        self.df["OutOfWater"] = self.df.apply(
            lambda r: ((r.WaterDepth - r.name[1]) < threshold) and (r.name[1] > min_hah),  # depth - hah
            axis=1)
        r_df = self.df.reset_index()
        # idx = pd.IndexSlice
        r_df.loc[
            ((r_df.Height > min_hah) & (r_df.OutOfWater)),
            vars_nan] = np.NaN
        r_df.loc[
            ((r_df.IBurst_Correlation_Beam < 50) & (r_df.Height <= min_hah)),
            vars_nan] = np.NaN
        self.df = r_df.set_index(['Date', 'Height'])

    def clean_by_correlation(self):
        self.df["Corr"] = self.df.apply(
                lambda r: r.IBurst_Correlation_Beam < 80,
                axis=1)
        self.df["minHeight"] = self.df.apply(
                lambda r: self.df.loc[
                    r.name[0], ].query("Corr == True").index.min(),
                axis=1)
        vars_nan = self.VARS[-(len(self.VARS)-1):] + self.AMPLITUDES
        df_grouped = self.df.groupby("Date")
        for d, df in df_grouped:
            # df[(df.index.get_level_values("Height") > df.minHeight.min()),
            #     vars_nan] = np.NaN
            lower_idx = list(filter(lambda x: x > df.minHeight.min(),
                                    self.HEIGHTS))
            self.df.loc[(d, lower_idx), vars_nan] = np.NaN
            # self.df = self.df.update(df, overwrite=True)

    def __str__(self):
        return "Signature1000 %s" % self.site

    def plot_magnitude(self):
        dfwindlist = station.get_weekly_wind()
        weeks = self.df.index.get_level_values('Date').week
        i = 0
        for week, df in self.df.groupby(weeks):
            dfwind = dfwindlist[i]
            fig, axes = plt.subplots(ncols=1, nrows=4,
                                     figsize=(28, 4), sharex=True)
            ax = axes[0]
            ax.scatter(dfwind.index, dfwind["speed"], s=4, c="black",
                       label="Wind speed\n[m/s]")
            ax.set_ylabel("Wind speed\n[m/s]")
            ax.set_yticks([0, 7, 14])
            ax.spines["left"].set_bounds(0, 14)
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax = ax.twinx()
            ax.scatter(dfwind.index, dfwind["direction"],
                       marker="x", label="Wind direction\n[degrees]")
            ax.set_ylabel("Wind direction\n[degrees]")
            ax.set_yticks([0, 90, 180, 270, 360])
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.35), frameon=False)
            ax.spines["right"].set_bounds(0, 360)
            ax.xaxis.set_visible(False)
            ax.spines["right"].set_position(("outward", 15))
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)
            # Temperature
            ax = axes[1]
            df_sen = self.wd[self.wd.index.week == week]
            ax.plot(df_sen.index, df_sen["Temperature"])
            ax.set_ylabel("Temperature [°C]")
            # Water depth
            ax = ax.twinx()
            ax.plot(df_sen.index, df_sen["WaterDepth"], linestyle=":",
                    color="black", label="Water Depth [m]")
            ax.set_ylabel("Water depth [m]")
            ax.set_ylim(bottom=0, top=self.wd["WaterDepth"].max())
            # Velocity magnitude & direction
            ax = axes[2]
            ax1 = axes[3]
            levels = ADCP_LEVELS[self.site - 1]
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
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax1.legend(loc="center left",
                       bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax.set_ylabel("Velocity\nspeed [m/s]")
            ax1.set_ylabel("Velocity\ndir. [°C]")
            fig.suptitle("%s - Week %s" % (str(self), i + 1))
            i += 1


class Aquadopp(object):
    """
    Represents an Aquadopp ADCP
    """
    VARS = ["a1", "a2", "a3",  # amplitudes
            "Vel_Mag", "Vel_Dir_TN",  # velocity mag. and dir
            "Vel_E_TN", "Vel_N_TN", "Vel_Up"]  # velocity components
    HEIGHTS = np.arange(0.3, 4.3, 0.1, dtype=np.float32)
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
        for v in self.VARS:
            df_vars[v] = []
        for i in range(0, len(ml_data["a1"])):
            for j in range(0, len(ml_data["a1"][i])):
                for v in self.VARS:
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
        index = list(itertools.product(timestamps, self.HEIGHTS))
        indx = pd.MultiIndex.from_tuples(index, names=['Date', 'Height'])
        df = pd.DataFrame(df_vars, indx, self.VARS)
        df = df.tz_localize(TIMEZONE, level=0)
        df = df.loc[ADCP_DATES["start"]:ADCP_DATES["end"]]
        self.df = df.join(self.wd, how="left")
        # clean data based on amplitude threshold
        if ADCP_A1_LEVELS[self.site - 1] is not None:
            self.df.loc[self.df.a1 < ADCP_A1_LEVELSS[self.site - 1],
                        self.VARS] = np.NaN
        if self.site == 3:  # clean based on hah
            self.df["OutOfWater"] = self.df.apply(
                lambda r: (r.WaterDepth - r.name[1]) < 0.8,  # depth - hah
                axis=1)
            self.df.loc[self.df.OutOfWater, self.VARS] = np.NaN
        # Sen file (temp, etc..)
        sen_folder = "Site{0}/{1}.sen".format(site, AQUADOPPS_SENS[site - 1])
        sen_datafile = os.path.join(FILEPATH, sen_folder)
        self.df_sen = pd.read_csv(sen_datafile, header=None, sep='\s+',
                                  parse_dates=[[0, 1, 2, 3, 4, 5]])
        self.df_sen.columns = ['date'] + self.SEN_HEADERS[-11:]
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
        for a in self.VARS[:3]:
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
        for v in self.VARS[-3:]:
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
            fig, axes = plt.subplots(ncols=1, nrows=4,
                                     figsize=(28, 4), sharex=True)
            ax = axes[0]
            ax.scatter(dfwind.index, dfwind["speed"], s=4, c="black",
                       label="Wind speed\n[m/s]")
            ax.set_ylabel("Wind speed\n[m/s]")
            ax.set_yticks([0, 7, 14])
            ax.spines["left"].set_bounds(0, 14)
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax = ax.twinx()
            ax.scatter(dfwind.index, dfwind["direction"],
                       marker="x", label="Wind direction\n[degrees]")
            ax.set_ylabel("Wind direction\n[degrees]")
            ax.set_yticks([0, 90, 180, 270, 360])
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.35), frameon=False)
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
            # Water depth
            ax = ax.twinx()
            wd_df = self.wd[self.wd.index.week == week]
            # wd_df.index = wd_df.index.strftime("%d-%m %H:%M")
            ax.plot(wd_df.index, wd_df["WaterDepth"], linestyle=":",
                    color="black", label="Water Depth [m]")
            ax.set_ylabel("Water depth [m]")
            ax.set_ylim(bottom=0, top=self.wd["WaterDepth"].max())
            # Velocity magnitude & direction
            ax = axes[2]
            ax1 = axes[3]
            levels = ADCP_LEVELS[self.site - 1]
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
            ax.legend(loc="center left",
                      bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax1.legend(loc="center left",
                       bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax.set_ylabel("Velocity\nspeed [m/s]")
            ax1.set_ylabel("Velocity\ndir. [°C]")
            fig.suptitle("%s - Week %s" % (str(self), i + 1))
            i += 1
