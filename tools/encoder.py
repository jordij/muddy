import logging
import numpy as np
import pandas as pd
import pyrsktools

from constants import (RAW_PATH, PROCESSED_PATH, H5_PATH, AVG_FOLDER,
                       VARIABLES, TIMEZONE, DEVICES)
from device import Device


def create_devices_by_type(dtype, dformat):
    """ Create all devices by type floater/bedframe """
    devices = []
    for d in DEVICES:
        if d["type"] == dtype:
            devices.append(Device(
                site=d["site"],
                dtype=d["type"],
                file=d["file"],
                f=d["freq"],
                sr=d["burst_samples"],
                i=d["interval"],
                T=d["T"],
                SSC=d["SSC"],
                dformat=dformat
            ))
    return devices


def create_device(site, dtype, origin):
    """ Create Device from dict values """
    d = next(item for item in DEVICES if item["site"] == site and item["type"] == dtype)
    return Device(
        site=d["site"],
        dtype=d["type"],
        file=d["file"],
        f=d["freq"],
        sr=d["burst_samples"],
        i=d["interval"],
        T=d["T"],
        SSC=d["SSC"],
        dformat=origin
    )


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
