import pandas as pd
import pyrsktools

from constants import (RAW_PATH, PROCESSED_PATH, H5_PATH, VARIABLES,
                       TIMEZONE, DEVICES)


def store_deviceH5(device, origin):
    """ RSK to H5 """
    if origin == "raw":
        datapath = "%s%s.rsk" % (RAW_PATH, device["file"])
    else:  # processed
        datapath = "%s%s_processed.rsk" % (
            PROCESSED_PATH, device["file"])
    with pyrsktools.open(datapath) as rsk:
        # Pandas dataframe for the win
        df = pd.DataFrame(rsk.npsamples())
        # timestamp as index, then UTC to NZ
        df = df.set_index("timestamp")
        df.index = df.index.tz_convert(TIMEZONE)
        # store df as HDF5
        df.to_hdf(
            "%s%s.h5" % (H5_PATH, device["file"]),
            key="df",
            mode="w")


def get_df_nvars(dataframe):
    """ Get num of rows (variables available in df) to print in plot """
    nvars = []
    for v in dataframe.columns:
        if v in VARIABLES.keys():
            nvars.append(VARIABLES[v])
    return nvars


def get_device(site):
    """ Get device from name - eg 'S1-f' or 'S2-bf' """
    return next(item for item in DEVICES if item["name"] == site)


def get_devices_by_type(dtype):
    """ Get devices by type floater/bedframe """
    return [item for item in DEVICES if item["type"] == dtype]


def get_df(device, origin):
    """ Get DataFrame given a device and an origin (filetype RSK or H5)"""
    df = None
    if origin == "h5":
        datapath = "%s%s.h5" % (H5_PATH, device["file"])
        print("Using %s as a dataframe source for %s %s" %
              (datapath, device["name"], device["type"]))
        df = pd.read_hdf(datapath, "df")
        print(df.shape)
        print("Any NaN values? -> %s" % str(df.isnull().T.any().T.sum()))
    else:  # rsk
        if origin == "raw":
            datapath = "%s%s.rsk" % (RAW_PATH, device["file"])
        else:  # processed
            datapath = "%s%s_processed.rsk" % (
                PROCESSED_PATH, device["file"])
        print("Using %s as a dataframe source." % datapath)
        rsk = pyrsktools.open(datapath)
        # Pandas dataframe for the win
        df = pd.DataFrame(rsk.npsamples())
        # timestamp as index, then UTC to NZ
        df = df.set_index("timestamp")
        df.index = df.index.tz_convert(TIMEZONE)
    return df
