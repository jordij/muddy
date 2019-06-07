import gc
import fire
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import pyrsktools
import seaborn as sns
from pandas.plotting import register_matplotlib_converters

from constants import OUTPUT_PATH, RAW_PATH, PROCESSED_PATH, HD5_PATH
from constants import VARIABLES, DEVICES, SITES
from maps import plot_bathymetry, plot_sites, plot_transect
from structure import create_structure

register_matplotlib_converters()


class Muddy(object):
    """" Main class """

    def __get_variables__(self, dataframe):
        """ Get num of rows (variables available in df) to print in plot """
        nvars = []
        for v in dataframe.columns:
            if v in VARIABLES.keys():
                nvars.append(VARIABLES[v])
        return nvars

    def __get_dataframe__(self, device, origin):
        """ Get DataFrame given a device and an origin (filetype RSK or H5)"""
        df = None
        if origin == "h5":
            datapath = "%s%s.h5" % (HD5_PATH, device['file'])
            print("Using %s as a dataframe source." % datapath)
            df = pd.read_hdf(datapath, 'df')
        else:  # rsk
            if origin == "raw":
                datapath = "%s%s.rsk" % (RAW_PATH, device['file'])
            else:  # processed
                datapath = "%s%s_processed.rsk" % (
                    PROCESSED_PATH, device['file'])
            print("Using %s as a dataframe source." % datapath)
            rsk = pyrsktools.open(datapath)
            # Pandas dataframe for the win
            df = pd.DataFrame(rsk.npsamples())
            # timestamp as index, then UTC to NZ
            df = df.set_index("timestamp")
            df.index = df.index.tz_convert('Pacific/Auckland')
        return df

    def __plot_all__(self, df, date, nvars, dest_file):
        """ Plot all daily vars in same figure """
        fig, axes = plt.subplots(ncols=1, nrows=len(nvars), sharex=True)
        df.plot(subplots=True, linewidth=0.25, ax=axes)
        idx = 0
        for ax in axes:
            ax.xaxis.set_major_locator(
                mdates.HourLocator(byhour=range(0, 24, 1)))
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter('%H:%M', tz=df.index.tz))
            ax.tick_params(axis='y', which='major', labelsize=10)
            ax.tick_params(axis='y', which='minor', labelsize=8)
            ax.tick_params(axis='x', which='major', labelsize=10)
            ax.tick_params(axis='x', which='minor', labelsize=8)
            # set name and units for each var/axes
            ax.set(xlabel='%s' % str(date), ylabel=nvars[idx]["units"])
            ax.legend([nvars[idx]["name"]])
            idx += 1
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

#    def __plot_single__(self, df, df_date, nrows, dest_folder):
#        """ Plot single daily vars in separate figures """
#        # TEMPERATURES
#        for temp in TEMPS:
#            if temp[0] in df.columns:
#                fig, ax = plt.subplots()
#                ax.plot(df.index, df[temp[0]], linewidth=0.5)
#                ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 1)))
#                ax.xaxis.set_major_formatter(
#                    mdates.DateFormatter('%H:%M', tz=df.index.tz))
#                ax.tick_params(
#                    axis='y', which='major', labelsize=6)
#                ax.tick_params(
#                    axis='y', which='minor', labelsize=4)
#                ax.tick_params(
#                    axis='x', which='major', labelsize=6)
#                ax.tick_params(
#                    axis='x', which='minor', labelsize=4)
#                ax.set(
#                    xlabel='Time',
#                    ylabel='°C',
#                    title='%s %s' % (df_date, temp[1]))
#                ax.yaxis.set_ticks(np.arange(-5, 30, 5))
#                ax.margins(x=0.01)
#                fig.autofmt_xdate()
#                fig.tight_layout()
#                plt.savefig(
#                    "%s/%s/%s_raw.png" % (
#                        dest_folder,
#                        temp[0],
#                        df_date),
#                    dpi=200)
#                plt.close()
#
#        # CONDUCTIVITY
#        if CONDUC[0] in df.columns:
#            fig, ax = plt.subplots()
#            ax.plot(
#                df.index, df[CONDUC[0]], linewidth=0.5)
#            ax.xaxis.set_major_locator(
#                mdates.HourLocator(byhour=range(0, 24, 1)))
#            ax.xaxis.set_major_formatter(
#                mdates.DateFormatter('%H:%M', tz=df.index.tz))
#            ax.tick_params(axis='y', which='major', labelsize=6)
#            ax.tick_params(axis='y', which='minor', labelsize=4)
#            ax.tick_params(axis='x', which='major', labelsize=6)
#            ax.tick_params(axis='x', which='minor', labelsize=4)
#            ax.set(
#                xlabel="Time",
#                ylabel=CONDUC[2],
#                title='%s %s' % (df_date, CONDUC[1]))
#            ax.margins(x=0.01)
#            fig.autofmt_xdate()
#            fig.tight_layout()
#            plt.savefig(
#                "%s/%s/%s_raw.png" % (
#                    dest_folder,
#                    CONDUC[0],
#                    df_date),
#                dpi=200)
#            plt.close()
#
#        # TURBIDITY
#        if TURBID[0] in df.columns:
#            fig, ax = plt.subplots()
#            ax.plot(
#                df.index, df[TURBID[0]], linewidth=0.5)
#            ax.xaxis.set_major_locator(
#                mdates.HourLocator(byhour=range(0, 24, 1)))
#            ax.xaxis.set_major_formatter(
#                mdates.DateFormatter('%H:%M', tz=df.index.tz))
#            ax.tick_params(axis='y', which='major', labelsize=6)
#            ax.tick_params(axis='y', which='minor', labelsize=4)
#            ax.tick_params(axis='x', which='major', labelsize=6)
#            ax.tick_params(axis='x', which='minor', labelsize=4)
#            ax.set(
#                xlabel="Time",
#                ylabel=TURBID[2],
#                title='%s %s' % (df_date, TURBID[1]))
#            ax.margins(x=0.01)
#            fig.autofmt_xdate()
#            fig.tight_layout()
#            plt.savefig(
#                "%s/%s/%s_raw.png" % (
#                    dest_folder,
#                    TURBID[0],
#                    df_date),
#                dpi=200)
#            plt.close()
#
#        # PRESSURE
#        if PRESS[0] in df.columns:
#            fig, ax = plt.subplots()
#            ax.plot(df.index, df[PRESS[0]], linewidth=0.5)
#            ax.xaxis.set_major_locator(
#                mdates.HourLocator(byhour=range(0, 24, 1)))
#            ax.xaxis.set_major_formatter(
#                mdates.DateFormatter('%H:%M', tz=df.index.tz))
#            ax.tick_params(axis='y', which='major', labelsize=6)
#            ax.tick_params(axis='y', which='minor', labelsize=4)
#            ax.tick_params(axis='x', which='major', labelsize=6)
#            ax.tick_params(axis='x', which='minor', labelsize=4)
#            ax.set(
#                xlabel="Time",
#                ylabel=PRESS[2],
#                title='%s %s' % (df_date, PRESS[1]))
#            ax.margins(x=0.01)
#            fig.autofmt_xdate()
#            fig.tight_layout()
#            plt.savefig(
#                "%s/%s/%s_raw.png" % (
#                    dest_folder,
#                    PRESS[0],
#                    df_date),
#                dpi=200)
#            plt.close()
#        # free mem
#        del df
#        gc.collect()

    def __store_deviceH5__(self, device, origin):
        if origin == "raw":
            datapath = "%s%s.rsk" % (RAW_PATH, device['file'])
        else:  # processed
            datapath = "%s%s_processed.rsk" % (
                PROCESSED_PATH, device['file'])
        with pyrsktools.open(datapath) as rsk:
            # Pandas dataframe for the win
            df = pd.DataFrame(rsk.npsamples())
            # timestamp as index, then UTC to NZ
            df = df.set_index("timestamp")
            df.index = df.index.tz_convert('Pacific/Auckland')
            # store df as HDF5
            df.to_hdf(
                '%s%s.h5' % (HD5_PATH, device['file']),
                key='df',
                mode='w')

    def daily_plots(self, origin="h5"):
        """ Generate daily plots """
        if isinstance(origin, str):
            if origin not in ["h5", "rsk"]:
                raise ValueError("String 'hd' or 'rsk' value expected.")
        else:
            raise TypeError("String 'hd' or 'rsk' value expected.")
        # Use seaborn style defaults and set the default figure size
        sns.set(rc={'figure.figsize': (12, 12)})
        for d in DEVICES:
            df = self.__get_dataframe__(d, origin)
            dflist = [group for group in df.groupby(df.index.date)]
            nvars = self.__get_variables__(df)
            for date, dfday in dflist:
                dest_file = "%s%s/%s/%s.png" % (
                    OUTPUT_PATH,
                    d['name'],
                    d['type'],
                    str(date))
                self.__plot_all__(dfday, date, nvars, dest_file)

    def map_plots(self):
        plot_transect()
        plot_sites()
        plot_bathymetry()

    def storeH5(self, origin="processed", site="all"):
        """ Store raw data in h5 to read/write heaps faster than .rsk"""
        if isinstance(origin, str):
            if origin not in ["processed", "raw"]:
                raise ValueError("String 'processed' or 'raw' value expected.")
        else:
            raise TypeError("String 'processed' or 'raw' value expected.")
        if site not in SITES + ["all"]:
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one site (1 to 5)
            dsite = next(item for item in DEVICES if item["name"] == site)
            self.__store_deviceH5__(dsite, origin)
        else:
            for d in DEVICES:
                self.__store_deviceH5__(d, origin)

    def create_struct(self):
        create_structure()


if __name__ == '__main__':
    fire.Fire(Muddy)
