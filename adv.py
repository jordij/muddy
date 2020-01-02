import os
import gsw
import pandas as pd
import scipy.io as sio
from constants import TIMEZONE
import numpy as np
import matplotlib.pyplot as plt

FILEPATH = "./data/Currents/ADV/"  # relative


class ADV(object):
    COL_NAMES = [
        "Burst counter",
        "Ensemble counter",
        "Velocity (Beam1|X|East)",
        "Velocity (Beam2|Y|North)",
        "Velocity (Beam3|Z|Up)",
        "Amplitude (Beam1)",
        "Amplitude (Beam2)",
        "Amplitude (Beam3)",
        "SNR (Beam1)",
        "SNR (Beam2)",
        "SNR (Beam3)",
        "Correlation (Beam1)",
        "Correlation (Beam2)",
        "Correlation (Beam3)",
        "Pressure",
        "Analog input 1",
        "Analog input 2",
        "Checksum"
    ]

    def __init__(self, site):
        self.site = site
        df_h5_file = '%sFoTWEL0%d.h5' % (FILEPATH, site)
        df_avg_h5_file = '%sFoTWEL0%d_avg.h5' % (FILEPATH, site)
        if not os.path.isfile(df_h5_file):
            self._load_raw_data()
        else:
            self.df = pd.read_hdf(df_h5_file, "df")
            self.df_avg = pd.read_hdf(df_avg_h5_file, "df")

    def _set_velocity(self):
        self.df_avg['V_dir'] = np.degrees(np.arctan2(
            self.df_avg['Velocity (Beam2|Y|North)'],
            self.df_avg['Velocity (Beam1|X|East)']))
        self.df_avg['V_dir'] = np.where(
            self.df_avg['V_dir'] < 0,
            self.df_avg['V_dir'] + 360,
            self.df_avg['V_dir'])
        self.df_avg['V_dir'] = (-self.df_avg['V_dir'] + 90) % 360
        qn_sq = np.power(self.df_avg['Velocity (Beam2|Y|North)'], 2)
        qe_sq = np.power(self.df_avg['Velocity (Beam1|X|East)'], 2)
        self.df_avg['V_magnitude'] = np.sqrt(qn_sq + qe_sq)

    def _clean(self):
        self.df_avg[self.df_avg['Correlation (Beam2)'] < 50] = np.NaN
        self.df_avg[self.df_avg['Correlation (Beam1)'] < 50] = np.NaN

    def _set_date(self):
        datafile = os.path.join(FILEPATH, "S{0}_WLonly.mat".format(self.site))
        ml_data = sio.loadmat(datafile)

        # MATLAB datenum to Python
        timestamps = []
        timestamps_avg = []
        timestamps.append(
            pd.to_datetime(ml_data["S1_WL"][0][0][0][0][0]-719529, unit='D'))
        timestamps_avg.append(timestamps[0])
        for i in range(1, len(ml_data["S1_WL"][0][0][0])):
            t = pd.to_datetime(ml_data["S1_WL"][0][0][0][i][0]-719529, unit='D')
            timestamps.append(t)
            if i % 2048 == 0:
                t = t - pd.Timedelta(
                    microseconds=t.microsecond)
                t = t - pd.Timedelta(
                    nanoseconds=t.nanosecond)
                timestamps_avg.append(t)
        t = t - pd.Timedelta(
                    microseconds=t.microsecond)
        t = t - pd.Timedelta(
                    nanoseconds=t.nanosecond)
        timestamps_avg.append(t)

        self.df['Date'] = pd.Series(timestamps)
        self.df = self.df.set_index('Date')
        self.df.index = self.df.index.tz_localize(TIMEZONE)
        self.df_avg['Date'] = pd.Series(timestamps_avg)
        self.df_avg = self.df_avg.set_index('Date')
        self.df_avg.index = self.df_avg.index.tz_localize(TIMEZONE)

    def _load_raw_data(self):
        folder = "S{0}_WLonly.mat".format(self.site)
        df_h5_file = '%sFoTWEL0%d.h5' % (FILEPATH, self.site)
        df_avg_h5_file = '%sFoTWEL0%d_avg.h5' % (FILEPATH, self.site)
        self.df = pd.read_csv(
            '%sFoTWEL0%d.dat' % (FILEPATH, self.site),
            header=None,
            sep=r"\s+",
            names=self.COL_NAMES)
        self.df_avg = self.df.groupby("Burst counter").mean()
        self._clean()
        self._set_date()
        self._set_velocity()
        self.df.to_hdf(df_h5_file, key="df", mode="w")
        self.df_avg.to_hdf(df_avg_h5_file, key="df", mode="w")

    def plot_velocity(self):
        fig, ax = plt.subplots()
        self.df_avg = self.df_avg[:-1]
        self.df_avg = self.df_avg[:-1]
        'Correlation (Beam2)'
        ax.scatter(self.df_avg.index, self.df_avg['V_dir'])

    def plot_bursts(self, indexes):

        for i in indexes:
            df = self.df[self.df['Burst counter'] == i]
            fig, axes = plt.subplots(nrows=2)
            axes[0].plot(df['Ensemble counter'], df['Velocity (Beam1|X|East)'], color="green", label="X-East")
            axes[1].plot(df['Ensemble counter'], df['Velocity (Beam2|Y|North)'], color="blue", label="X-East")

    def plot_magnitude(self):
        self.df_avg["depth"] = self.df_avg.apply(
            lambda r:  -gsw.conversions.z_from_p(
                r.Pressure, -37.213110),
            axis=1)
        # dfwindlist = station.get_weekly_wind()
        weeks = self.df_avg.index.get_level_values('Date').week
        i = 0
        for week, df in self.df_avg.groupby(weeks):
            # dfwind = dfwindlist[i]
            fig, axes = plt.subplots(ncols=1, nrows=3,
                                     figsize=(28, 4), sharex=True)
            # ax = axes[0]
            # ax.scatter(dfwind.index, dfwind["speed"], s=4, c="black",
                       # label="Wind speed\n[m/s]")
            # ax.set_ylabel("Wind speed\n[m/s]")
            # ax.set_yticks([0, 7, 14])
            # ax.spines["left"].set_bounds(0, 14)
            # ax.legend(loc="center left",
            #           bbox_to_anchor=(-0.155, 0.65), frameon=False)
            # ax = ax.twinx()
            # ax.scatter(dfwind.index, dfwind["direction"],
            #            marker="x", label="Wind direction\n[degrees]")
            # ax.set_ylabel("Wind direction\n[degrees]")
            # ax.set_yticks([0, 90, 180, 270, 360])
            # ax.legend(loc="center left",
            #           bbox_to_anchor=(-0.155, 0.35), frameon=False)
            # ax.spines["right"].set_bounds(0, 360)
            # ax.xaxis.set_visible(False)
            # ax.spines["right"].set_position(("outward", 15))
            # ax.spines["top"].set_visible(False)
            # ax.spines["bottom"].set_visible(False)
            # ax.spines["left"].set_visible(False)
            # Temperature
            # ax = axes[1]
            # df_sen = self.df_sen[self.df_sen.index.week == week]
            # ax.plot(df_sen.index, df_sen["Temperature"])
            # ax.set_ylabel("Temperature [°C]")
            # # Water depth
            # ax = ax.twinx()
            # wd_df = self.wd[self.wd.index.week == week]
            # # wd_df.index = wd_df.index.strftime("%d-%m %H:%M")
            # ax.plot(wd_df.index, wd_df["WaterDepth"], linestyle=":",
            #         color="black", label="Water Depth [m]")
            # ax.set_ylabel("Water depth [m]")
            # ax.set_ylim(bottom=0, top=self.wd["WaterDepth"].max())
            # Velocity magnitude & direction
            ax = axes[0]
            ax1 = axes[1]
            ax2 = axes[2]
            # levels = ADCP_LEVELS[self.site - 1]
            # subdf = df.loc[pd.IndexSlice[:, levels[0]], :]
            # subdf.index = subdf.index.droplevel(level=1)  # drop height
            ax2.plot(df.index, df["depth"],
                     color="black", label='depth', linestyle=":")
            ax.plot(df.index, df["V_magnitude"],
                    color="blue", label='V magnitude')
            ax1.scatter(df.index, df["V_dir"],
                        color="blue", label='V direction', s=3)
            # subdf = df.loc[pd.IndexSlice[:, levels[1]], :]
            # subdf.index = subdf.index.droplevel(level=1)  # drop height
            # ax.plot(subdf.index, subdf["Vel_Mag"],
            #         color="red", label='%.1f mab' % levels[1])
            # ax1.scatter(subdf.index, subdf["Vel_Dir_TN"],
            #             color="red", label='%.1f mab' % levels[1], s=3)
            # subdf = df.loc[pd.IndexSlice[:, levels[2]], :]
            # subdf.index = subdf.index.droplevel(level=1)  # drop height
            # ax.plot(subdf.index, subdf["Vel_Mag"],
            #         color="green", label='%.1f mab' % levels[2])
            # ax1.scatter(subdf.index, subdf["Vel_Dir_TN"],
            #             color="green", label='%.1f mab' % levels[2], s=3)
            # ax.legend(loc="center left",
            #           bbox_to_anchor=(-0.155, 0.65), frameon=False)
            # ax1.legend(loc="center left",
            #            bbox_to_anchor=(-0.155, 0.65), frameon=False)
            ax.set_ylabel("Velocity\nspeed [m/s]")
            ax1.set_ylabel("Velocity\ndirection [°C]")
            fig.suptitle("Week %d" % (i + 1))
            i += 1

    def plot_rose(self):
        import seaborn as sns
        from windrose import plot_windrose

        sns.set(rc={"figure.figsize": (24, 16)})
        sns.set_style("ticks")
        # set_font_sizes(big=False)
        ax = plot_windrose(self.df_avg, kind='bar', bins=np.arange(0, 0.2, 0.025),
                           normed=True, opening=0.8,
                           var_name="V_magnitude", direction_name="V_dir")
        # ax.set_yticks([])  # remove % labels
        # ax.get_legend().remove()
        # plt.axis('off')
        # legend = ax.set_legend(bbox_to_anchor=(-1, -1))
        legend = ax.set_legend(
            bbox_to_anchor=(-0.25, 0.55),
            # loc='upper left',
            title="V [m/s]")
        labels = [
            u"0 ≤ V < 0.025",
            u"0.025 ≤ V < 0.05",
            u"0.05 ≤ V < 0.075",
            u"0.075 ≤ V < 0.1",
            u"0.1 ≤ V < 0.125",
            u"0.125 ≤ V < 0.15",
            u"0.15 ≤ V < 0.175",
            u"Q ≥ 0.175"]
        for i, l in enumerate(labels):
            legend.get_texts()[i].set_text(l)
        # plt.savefig("./plots/fluxes/flux_%s" % filename, dpi=300, transparent=True)
