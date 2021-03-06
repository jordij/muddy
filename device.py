import logging
import numpy as np
import os.path
import pandas as pd
import pyrsktools

from burst import BurstFourier, BurstWelch, BurstPeaks
from constants import (H5_PATH, OUTPUT_PATH, PROCESSED_PATH, VARIABLES,
                       TIMEZONE, AVG_FOLDER, Z_ELEVATION, DEVICES)
from intervals import DATA_INTERVALS, CALM_INTERVALS, STORM_INTERVALS
from tools import plotter, station


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
        self.dtype = dtype
        self._init_logger()
        if dtype not in ["floater", "bedframe"]:
            raise ValueError("Unknown device type")
        if dformat not in ["rsk", "h5"]:
            raise ValueError("Unknown data format type")
        self.file = file
        self.f = f
        self.sr = sr
        self.i = i
        self.z = Z_ELEVATION
        self.df_tidal = None
        if len(T) != len(SSC):
            raise ValueError("T and SSC must have the same length")
        self.T = T
        self.SSC = SSC
        self.format = dformat
        self.vars = []
        self._load_data()

    def _init_logger(self):
        self.logger = logging.getLogger(str(self))
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            fh = logging.FileHandler("./logs/%s.log" % str(self))
            fh.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        self.logger.info("Device %s create" % str(self))

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
            self.set_tide()
            self.logger.info(
                "Using %s as a dataframe source for averaged %s",
                self.get_H5_avg_path(),
                str(self))
            self.logger.info(self.df_avg.shape)
            self.logger.info(
                "NAN values: %s",
                str(self.df_avg.isnull().T.any().T.sum()))
        else:  # rsk
            data_path = self.get_RSK_path()
            rsk = pyrsktools.open(data_path)
            # Pandas dataframe for the win
            self.df = pd.DataFrame(rsk.npsamples())
            # timestamp as index, localize it as NZST
            self.df = self.df.set_index("timestamp")
            self.df.index = self.df.index.tz_convert(None)
            self.df.index = self.df.index.tz_localize(TIMEZONE)
            self.set_ssc()
        self.logger.info(
            "Using %s as a dataframe source for %s",
            data_path,
            str(self))
        self.logger.info(self.df.shape)
        self.logger.info(
            "NAN values: %s",
            str(self.df.isnull().T.any().T.sum()))
        self._set_vars()

    def _calc_bursts(self):
        """
        Calculates U, T and H for each valid burst.
        Note: only available for bedframe devices.
        """
        # Orbital speed, sig wave height and period
        if self.dtype != "bedframe":
            raise NotImplementedError("Not available in current class")
        self.df_avg["u"] = np.NaN
        self.df_avg["T"] = np.NaN
        self.df_avg["H"] = np.NaN
        df = self.clean_df(self.df, average=False)
        # Calculate U for each available burst
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
            else:
                self.logger.warning("Invalid burst start date %s end date %s",
                                    str(start_date),
                                    str(end_date))
            start_date = end_date

    def set_tide(self):
        """
        Calculate trend of tide Ebb/Flood depending on next row's depth
        """
        if "Tide" not in self.df_avg.columns:
            self.df_avg["Tide"] = np.where(
                self.df_avg["depth_00"] > self.df_avg["depth_00"].shift(-1),
                "Ebb",
                "Flood")
        # last row doesn't have a next, compare with previous row
        last_rows = self.df_avg.tail(2)
        if last_rows.iloc[0].depth_00 > last_rows.iloc[1].depth_00:
            self.df_avg.at[self.df_avg.index[-1], "Tide"] = "Ebb"
        else:
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
            # S1 floater saturated, remove max values
            if self.site == "S1" and self.dtype == "floater":
                d = self.get_dict_device()
                self.df.loc[
                    self.df["ssc"] == d["ssc_saturated_value"], ["ssc"]
                    ] = np.NaN

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
        bvars = [
            "salinity_00",
            "temperature_00",
            "seapressure_00",
            "depth_00"]
        dfburst = df[(df.index >= start) & (df.index < end)][:self.sr][bvars]
        # discard burst with missing values or NaN
        if ((len(dfburst) < (self.sr/2)) or
            (dfburst.isnull().values.sum() != 0) or
                (dfburst.isna().values.sum() != 0)):
            return None
        if method == "fourier":
            return BurstFourier(
                dfburst, dfburst.index, self.f, self.z, str(self))
        elif method == "welch":
            return BurstWelch(
                dfburst, dfburst.index, self.f, self.z, str(self))
        else:
            return BurstPeaks(
                dfburst, dfburst.index, self.f, self.z, str(self))

    def set_df_avg(self, save=False):
        """
        Calculates SSC, clean data, average and save pandas.DataFrame
        in self.data_path_avg file
        """
        self.set_ssc()
        self.df_avg = self.clean_df(self.df)
        self.df_avg["ssc_sd"] = self.df.ssc.resample("%ss" % self.i).std()
        if self.dtype == "bedframe":
            self._calc_bursts()
        self.save_H5(avg=save)

    def clean_df(self, df, average=True):
        """ Clean and average given dataframe df """
        intervals = DATA_INTERVALS[self.__str__()]
        if average:
            df = df.resample("%ss" % self.i, label="left").mean()
            dfr = pd.DataFrame(
                    index=df.index,
                    columns=df.columns) if intervals else df
        else:
            dfr = pd.DataFrame(columns=df.columns) if intervals else df
        if intervals:
            for interval in intervals:
                if average:
                    dfr.update(df[interval[0]:interval[1]])
                else:
                    dfr = dfr.append(df[interval[0]:interval[1]])
        # just in case some dodgy data sneaked into the intervals
        dfr.loc[dfr.turbidity_00 < 0, "turbidity_00"] = np.nan
        return dfr

    def get_depth_stats(self):
        """
        Burst-averaged mean, max, min values of Depth [m]
        """
        return (round(self.df_avg.depth_00.mean(), 2),
                round(self.df_avg.depth_00.max(), 2),
                round(self.df_avg.depth_00.min(), 2))

    def get_wave_stats(self):
        """
        Burst-averaged mean, max, min values of sig wave height [m]
        """
        return (round(self.df_avg[self.df_avg.H > 0].H.mean(), 2),
                round(self.df_avg[self.df_avg.H > 0].H.max(), 2),
                round(self.df_avg[self.df_avg.H > 0].H.min(), 2))

    def get_period_stats(self):
        """
        Burst-averaged mean, max, min values of peak period [s]
        """
        return (round(self.df_avg[self.df_avg["T"] > 0]["T"].mean(), 2),
                round(self.df_avg[self.df_avg["T"] > 0]["T"].max(), 2),
                round(self.df_avg[self.df_avg["T"] > 0]["T"].min(), 2))

    def get_u_stats(self):
        """
        Burst-averaged mean, max, min values of orbital velocity [cm/s]
        """
        return (round(self.df_avg[self.df_avg["u"] > 0]["u"].mean(), 2),
                round(self.df_avg[self.df_avg["u"] > 0]["u"].max(), 2),
                round(self.df_avg[self.df_avg["u"] > 0]["u"].min(), 2))

    def get_ssc_stats(self):
        """
        Burst-averaged mean, max, min values of SSC [mg/l]
        """
        return (round(self.df_avg[self.df_avg["ssc"] > 0.01]["ssc"].mean(), 4),
                round(self.df_avg[self.df_avg["ssc"] > 0.01]["ssc"].max(), 4),
                round(self.df_avg[self.df_avg["ssc"] > 0.01]["ssc"].min(), 4))

    def get_time_stats(self):
        """
        Get % of time in the water (depth available)
        """
        perc = (len(self.df_avg[self.df_avg.depth_00 > 0.025]) /
                len(self.df_avg)) * 100
        self.logger.info("Time in the water %f", perc)
        return round(perc, 2)

    def get_dict_device(self):
        """ Return dict element defined in constants file """
        return next(item for item in DEVICES if (item["site"] == self.site and
                    item["type"] == self.dtype))

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
            title = "%s %s" % (str(self), str(date))
            # averaged turb and depth (W/O cleaning it)
            dest_file = "%s%s/%s/%s/%s.png" % (
                OUTPUT_PATH,
                self.site,
                self.dtype,
                AVG_FOLDER,
                str(date))
            dfr = dfday.resample("%ss" % self.i).mean()
            plotter.plot_hourly_ssc_depth_avg(
                dfr[["ssc", "depth_00"]],
                date,
                dest_file,
                title)
            if self.df_avg is not None:
                # averaged CLEAN turb and depth
                dfr = self.df_avg[self.df_avg.index.date == date]
                parts = dest_file.split(".")
                dest_file = ".".join(parts[:-1]) + "_clean" + "." + parts[-1]
                plotter.plot_hourly_ssc_depth_avg(
                    dfr[["ssc", "depth_00"]],
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
        """ Plots SSC vs wave orbital velocity """
        dest_file = "%s%s/%s/%s/%s_%s_ssc_vs_u.png" % (
            OUTPUT_PATH,
            self.site,
            self.dtype,
            AVG_FOLDER,
            self.site.lower(),
            self.dtype.lower())
        plotter.plot_ssc_u(self.df_avg, dest_file, str(self))
        dest_file = "%s%s/%s/%s/%s_%s_ssc_vs_u_log.png" % (
            OUTPUT_PATH,
            self.site,
            self.dtype,
            AVG_FOLDER,
            self.site.lower(),
            self.dtype.lower())
        plotter.plot_ssc_u_log(self.df_avg, dest_file, str(self))

    def plot_ssc_u_h(self, dffl=None):
        """ Plots a time series for SSC, Sig wave height and water depth """
        dest_file = "%s%s/%s/%s/%s_ssc_u_h_series.png" % (
            OUTPUT_PATH,
            self.site,
            self.dtype,
            AVG_FOLDER,
            str(self).lower())
        plotter.plot_ssc_u_h_series(self.df_avg, dffl, dest_file, str(self))

    def plot_ssc_u_h_weekly(self, dffl=None):
        """ Plots a detailed weekly times series """
        dfwindlist = station.get_weekly_wind()
        dfrainlist = station.get_weekly_rainfall()
        dfpressurelist = station.get_weekly_pressure()
        dfrivers = station.get_weekly_rivers()
        dflist = [g for g in self.df_avg.groupby(self.df_avg.index.week)]
        if dffl is not None:
            dffllist = [g for g in dffl.groupby(dffl.index.week)]
        else:
            dffllist = [[None, None] for i in dflist]
        depthlist = self.get_weekly_corrected_depth()
        i = 0
        for date, dfweek in dflist:
            dfriverlist = [(k, val[i]) for k, val in dfrivers.items()]
            dest_file = "%s%s/%s/%s/weekly_ssc_u_h_series_%d.png" % (
                OUTPUT_PATH,
                self.site,
                self.dtype,
                AVG_FOLDER,
                i)
            dfweek["u"] = dfweek["u"].fillna(-1)
            plotter.plot_ssc_u_h_weekly_series(
                dfweek,
                dffllist[i][1],
                dfwindlist[i],
                dfrainlist[i],
                dfpressurelist[i],
                depthlist[i],
                dfriverlist,
                dest_file,
                date,
                str(self),
                i)
            i += 1

    def plot_depth(self):
        return plotter.plot_depth(self.df_avg)

    def get_weekly_corrected_depth(self):
        self.df["depth_corrected"] = self.df["depth_00"] - 0.15
        self.df.loc[self.df["depth_corrected"] < 0, ["depth_corrected"]] = 0
        return [g[1]["depth_corrected"].resample("%ss" % self.i).mean()
                for g in self.df.groupby(self.df.index.week)]

    def plot_tidal_ssc(self, intervals=None):
        """
        Plot SSC and U values per tidal cycle defined by given intervals.
        """
        if intervals is None:
            intervals = STORM_INTERVALS[self.__str__()]
        else:
            intervals = intervals[self.__str__()]
        tidal_vars = ["hours", "u", "ssc", "H", "depth_00", "T"]

        if self.df_tidal is None:
            tdelta = pd.Timedelta("300s")
            df_tidal = pd.DataFrame()
            for interval in intervals:
                df_int = self.df_avg[interval[0]:interval[1]]
                mid = df_int[df_int["Tide"] == "Ebb"].head(1).index[0] - tdelta
                df_int["hours"] = df_int.apply(
                    lambda r: get_hours(r, mid),
                    axis=1)
                df_tidal = df_tidal.append(df_int[tidal_vars])
                df_tidal["ssc"] = pd.to_numeric(df_tidal["ssc"])
            self.df_tidal = df_tidal
        plotter.plot_tidal_u_ssc(self.df_tidal, intervals)

    def get_intervals_df(self, intervals=None):
        """
        Plot SSC and U values per tidal cycle defined by given intervals.
        """
        if intervals is None:
            intervals = STORM_INTERVALS[self.__str__()]
        else:
            intervals = intervals[self.__str__()]
        tidal_vars = ["u", "ssc", "depth_00", "Tide"]

        if self.df_tidal is None:
            tdelta = pd.Timedelta("300s")
            df_tidal = pd.DataFrame()
            for interval in intervals:
                df_int = self.df_avg[interval[0]:interval[1]]
                # mid = df_int[df_int["Tide"] == "Ebb"].head(1).index[0] - tdelta
                # df_int["hours"] = df_int.apply(
                #     lambda r: get_hours(r, mid),
                #     axis=1)
                df_tidal = df_tidal.append(df_int[tidal_vars])
                df_tidal["ssc"] = pd.to_numeric(df_tidal["ssc"])
                df_tidal["depth_00"] = pd.to_numeric(df_tidal["depth_00"])
                df_tidal["site"] = self.site
                self.df_tidal = df_tidal
        return self.df_tidal


def get_hours(row, mid_value):
    """
    Get signed difference, in seconds, between row index (name)
    and given mid_value timestamp
    """
    if (row.name < mid_value):
        return -(mid_value - row.name).total_seconds()/3600
    else:
        return (row.name - mid_value).total_seconds()/3600
