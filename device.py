import numpy as np
import os.path
import pandas as pd
import pyrsktools

from burst import BurstFourier, BurstWelch, BurstPeaks
from constants import (H5_PATH, OUTPUT_PATH, PROCESSED_PATH, VARIABLES,
                       TIMEZONE, AVG_FOLDER, Z_ELEVATION)
from tools import plotter


class Device(object):
    r"""
    Represents a RbR Concerto and its associated data (if loaded)

    Parameters
    ----------
    site : str
        ['S1', .. 'S5']
    dtype : string
        'floater' or 'bedframe'
    file : str
        file name without extension
    f : int
        Sampling frequency [Hz]
    sr : int
        Sampling rate (samples per burst)
    i : int
        Interval between bursts [s]
    T : array_like
        Turbidity calibration values [NTU]
    SSC : array_like
        Suspended sediment concentration [mg/L]
        Same length as T
    dformat : string
        Data format "h5" or "rsk"
    """

    def __init__(self, site, dtype, file, f, sr, i, T, SSC, dformat):
        self.site = site
        if dtype not in ["floater", "bedframe"]:
            raise ValueError("Unknown device type")
        if dformat not in ["rsk", "h5"]:
            raise ValueError("Unknown data format type")
        self.dtype = dtype
        self.file = file
        self.f = f
        self.sr = sr
        self.i = i
        self.z = Z_ELEVATION
        if len(T) != len(SSC):
            raise ValueError("T and SSC must have the same length")
        self.T = T
        self.SSC = SSC
        self.format = dformat
        self.vars = []
        self._load_data()

    def _set_vars(self):
        """
        Set number of variables available in self.df pandas.DataFrame
        """
        if self.vars == []:
            for v in self.df.columns:
                if v in VARIABLES.keys():
                    self.vars.append(VARIABLES[v])

    def _load_data(self):
        """
        Loads data from device file into self.df as a pandas.DataFrame.
        Loads burst-averaged data into self.df_avg as a pandas.DataFrame.
        """
        self.df = None
        self.df_avg = None
        if self.format == "h5":
            data_path = self.get_H5_path()
            self.df = pd.read_hdf(data_path, "df")
            try:
                self.df_avg = pd.read_hdf(self.get_H5_avg_path(), "df")
            except FileNotFoundError:
                self.set_df_avg(save=True)
            finally:
                self.set_tide()
            print("Using %s as a dataframe source for averaged %s" %
                  (self.get_H5_avg_path(), str(self)))
            print(self.df_avg.shape)
            print("Any NaN values? -> %s" % str(self.df_avg.isnull().T.any().T.sum()))
        else:  # rsk
            data_path = self.get_RSK_path()
            rsk = pyrsktools.open(data_path)
            # Pandas dataframe for the win
            self.df = pd.DataFrame(rsk.npsamples())
            # timestamp as index, then UTC to NZ
            self.df = self.df.set_index("timestamp")
            self.df.index = self.df.index.tz_convert(TIMEZONE)
        print("Using %s as a dataframe source for %s" %
              (data_path, str(self)))
        print(self.df.shape)
        print("Any NaN values? -> %s" % str(self.df.isnull().T.any().T.sum()))
        self._set_vars()

    def set_tide(self):
        """
        Calculate trend of tide Ebb/Flood depending on next row's depth
        """
        # if "tide" not in self.df_avg.columns:
        self.df_avg["Tide"] = np.where(
                self.df_avg["depth_00"] > self.df_avg["depth_00"].shift(-1),
                "Ebb",
                "Flood")
        # last row doesn't have a next, compare with previous row
        last_rows = self.df_avg.tail(2)
        if last_rows.iloc[0].depth_00 > last_rows.iloc[1].depth_00:
            print("Last row is ebb %f" % last_rows.iloc[1].depth_00)
            self.df_avg.at[self.df_avg.index[-1], "Tide"] = "Ebb"
        else:
            print("Last row is flood %f" % last_rows.iloc[1].depth_00)
            self.df_avg.at[self.df_avg.index[-1], "Tide"] = "Flood"

    def set_ssc(self):
        """
        Calculate SSC from linear interpolation of self.T with self.SSC
        """
        if "ssc" not in self.df.columns:
            self.df["ssc"] = self.df.apply(
                lambda r: np.interp(
                    r.turbidity_00,
                    self.T,
                    self.SSC),
                axis=1)

    def save_H5(self, avg=False):
        """
        Saves device data to h5 file
        """
        if not os.path.isfile(self.get_H5_path()):
            self.df.to_hdf(self.get_H5_path(), key="df", mode="w")
        if avg:
            self.df_avg.to_hdf(self.get_H5_avg_path(), key="df", mode="w")

    def get_H5_path(self):
        return "%s%s.h5" % (H5_PATH, self.file)

    def get_H5_avg_path(self):
        return "%s%s/%s.h5" % (H5_PATH, AVG_FOLDER, self.file)

    def get_RSK_path(self):
        return "%s%s_processed.rsk" % (PROCESSED_PATH, self.file)

    def get_burst(self, start=None, end=None, method="fourier", df=None):
        """"
        Get Burst from start to end dates

        """
        if df is None:
            df = self.df
        burst_vars = [
            'salinity_00',
            'temperature_00',
            'seapressure_00',
            'depth_00']
        dfburst = df[start:end][:self.sr][burst_vars]

        if len(dfburst) == 0:
            return None
        if method == "fourier":
            return BurstFourier(dfburst, dfburst.index, self.f, self.z)
        elif method == "welch":
            return BurstWelch(dfburst, dfburst.index, self.f, self.z)
        else:
            return BurstPeaks(dfburst, dfburst.index, self.f, self.z)

    def set_df_avg(self, save=False):
        """
        Calculate SSC, clean data, average and save pandas.DataFrame
        in self.data_path_avg file
        """
        self.set_ssc()
        self.df_avg = self.clean_df(self.df)
        self.df_avg["ssc_sd"] = self.df.ssc.resample("%ss" % self.i).std()
        # Orbital speed, sig wave height and period
        self.df_avg["u"] = 0
        self.df_avg["T"] = 0
        self.df_avg["H"] = 0
        self.df_avg["burst_length"] = 0
        # Calculate U for each available burst
        df = self.clean_df(self.df, resample=False)
        start_date = self.df_avg.index[0]
        while start_date <= self.df_avg.index[-1]:
            end_date = start_date + pd.Timedelta("%ss" % self.i)
            burst = self.get_burst(
                        start=start_date,
                        end=end_date,
                        method="welch",
                        df=df)
            if burst:
                self.df_avg.loc[start_date, ["u", "T", "H"]] = burst.get_UTH()
                self.df_avg.loc[start_date, "burst_length"] = len(burst.df)
            start_date = end_date
        self.save_H5(avg=save)

    def clean_df(self, df, resample=True):
        """ Clean and average given dataframe df """
        df = df[df.salinity_00.notnull() & (df.salinity_00 > 0)]
        print("Length of dataset after cleaning salinity: %i" % len(df))
        df = df[df.turbidity_00.notnull() & (df.turbidity_00 > 5)]
        print("Length of dataset after cleaning turbidity: %i" % len(df))
        df = df[df.depth_00.notnull() & (df.depth_00 > 0)]
        print("Length of dataset after cleaning depth: %i" % len(df))
        if resample:
            return df.resample("%ss" % self.i, label='left').mean()
        else:
            return df

    def __str__(self):
        return ("%s %s") % (self.site, self.dtype.capitalize())

    def unicode(self):
        return self.__str__()

    def plot_days(self):
        dflist = [group for group in self.df.groupby(self.df.index.date)]
        for date, dfday in dflist:
            # all variables in the same plot
            dest_file = "%s%s/%s/%s.png" % (
                OUTPUT_PATH,
                self.site,
                self.dtype,
                str(date))
            plotter.plot_all_hourly(dest_file, date, dfday, self.vars)
            # averaged turb and depth (W/O cleaning it)
            dest_file = "%s%s/%s/%s/%s.png" % (
                OUTPUT_PATH,
                self.site,
                self.dtype,
                AVG_FOLDER,
                str(date))
            dfr = dfday.resample("%ss" % self.i).mean()
            title = "%s %s" % (str(self), str(date))
            plotter.plot_hourly_turb_depth_avg(
                dfr[["turbidity_00", "depth_00"]],
                date,
                dest_file,
                title)
            # averaged CLEAN turb and depth
            dfr = self.clean_df(dfday)
            parts = dest_file.split('.')
            dest_file = ".".join(parts[:-1]) + '_clean' + '.' + parts[-1]
            plotter.plot_hourly_turb_depth_avg(
                dfr[["turbidity_00", "depth_00"]],
                date,
                dest_file,
                title)

    def plot_avg(self):
        """
        Plot averaged-bursts of SSC vs depth and salinity
        """
        dest_file = "%s%s/%s/%s/ssc.png" % (
                OUTPUT_PATH,
                self.site,
                self.dtype,
                AVG_FOLDER)
        plotter.plot_ssc_avg(self.df_avg, dest_file, str(self))

    def plot_ssc_u(self):
        self.df_avg['u'] = self.df_avg['u'] * 100
        dest_file = "%s%s/%s/%s/ssc_vs_u.png" % (
            OUTPUT_PATH,
            self.site,
            self.dtype,
            AVG_FOLDER)
        plotter.plot_ssc_u(self.df_avg, dest_file, str(self))

    def plot_ssc_u_h(self):
        self.df_avg['u'] = self.df_avg['u'] * 100
        dest_file = "%s%s/%s/%s/ssc_u_h_series.png" % (
            OUTPUT_PATH,
            self.site,
            self.dtype,
            AVG_FOLDER)
        plotter.plot_ssc_u_h_series(self.df_avg, dest_file, str(self))
