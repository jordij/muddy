import numpy as np
import pandas as pd

from constants import INST_TYPES
from tools import encoder


def basic_stats():
    """
    Basic stats for set of concerto instruments
    """
    devs = []
    for t in INST_TYPES:  # all instruments
        for d in encoder.create_devices_by_type(t, "h5"):
            devs.append(d)
    index = [str(d) for d in devs]
    depth_cols = ["Mean depth [m]", "Max depth [m]", "Min depth [m]"]
    wave_cols = ["Mean Sig. Wave Height [m]", "Max Sig. Wave Height [m]",
                 "Min Sig. Wave Height [m]"]
    period_cols = ["Mean Peak period [s]", "Max Peak period [s]",
                   "Min Peak period [s]"]
    u_cols = ["Mean Orb. Vel. [cm/s]", "Max Orb. Vel. [cm/s]",
              "Min Orb. Vel. [cm/s]"]
    ssc_cols = ["Mean SSC [mg/l]", "Max SSC [mg/l]", "Min SSC [mg/l]"]
    columns = (["Site", "Type"] + depth_cols + wave_cols + period_cols + u_cols
               + ssc_cols + ["% Time in the water"])
    dfstats = pd.DataFrame(index=index, columns=columns)

    for d in devs:
        dfstats.loc[str(d), ["Site", "Type"]] = (d.site, d.dtype)
        dfstats.loc[str(d), depth_cols] = d.get_depth_stats()
        if d.dtype == "bedframe":
            dfstats.loc[str(d), wave_cols] = d.get_wave_stats()
            dfstats.loc[str(d), period_cols] = d.get_period_stats()
            dfstats.loc[str(d), u_cols] = d.get_u_stats()
        else:
            dfstats.loc[str(d), wave_cols] = [np.nan, np.nan, np.nan]
            dfstats.loc[str(d), u_cols] = [np.nan, np.nan, np.nan]
        dfstats.loc[str(d), ssc_cols] = d.get_ssc_stats()
        dfstats.loc[str(d), ["% Time in the water"]] = d.get_time_stats()
    return dfstats
