import numpy as np
import pandas as pd
from constants import FLUXES_PATH
from tools import plotter
from cmath import rect, phase


DZ = 0.1


def correct_angle(theta):
    """
    Transform negative to 0-360 range
    """
    if theta < 0:
        theta = theta + 360
    if theta == 0:
        theta = 360
    return theta


def mean_Vel_Dir_TN(df):
    """
    Wrapper for mean_angle with direction
    """
    return mean_angle(df["Vel_Dir_TN"])


def mean_angle(deg):
    """
    Mean angle between 2 angles in degrees
    """
    a = deg[0]
    b = deg[1]
    if np.isnan(a) and not np.isnan(b):
        return b
    elif not np.isnan(a) and np.isnan(b):
        return a
    elif np.isnan(a) and np.isnan(b):
        return np.NaN
    else:
        diff = ((a - b + 180 + 360) % 360) - 180
        angle = (360 + b + (diff / 2)) % 360
        # print("Average between %d and %d is %d" % (a, b, angle))
        return angle


def calc_flux(dfl, dbf, adcp, filename,
              heights, save=False, method="bedframe"):
    if method == "average":
        if dfl is not None:  # 1/h * SSC(avg)
            dbf['C'] = ((dbf.ssc + dfl.ssc)/2) * (1/dbf['depth_00'])
        else:  # 1/h * SSC
            dbf['C'] = dbf.ssc * (1/dbf['depth_00'])
        adcp_df = adcp  # use all bins available
    elif method == "bedframe":  # just 2 bottoms bins
        dbf['C'] = (dbf.ssc / 1000)  #* (1/dbf['depth_00'])  # mg/L to kg/m^3
        adcp_df = adcp.loc[pd.IndexSlice[:, heights], :]
    else:
        raise ValueError("Unkown method")
    # Q for N/S and E/W components
    dbf['U_avg'] = adcp_df.groupby(level=0).Vel_N_TN.mean()
    dbf['V_avg'] = adcp_df.groupby(level=0).Vel_E_TN.mean()
    dbf['Vel_Mag'] = adcp_df.groupby(level=0).Vel_Mag.mean()
    dbf['QN'] = dbf['C'] * dbf['U_avg'] * DZ  # kg/m^2/s
    dbf['QE'] = dbf['C'] * dbf['V_avg'] * DZ  # kg/m^2/s
    # Total Q and direction (degrees)
    qn_sq = np.power(dbf['QN'].astype(np.float32), 2)
    qe_sq = np.power(dbf['QE'].astype(np.float32), 2)
    dbf['Q'] = np.sqrt(qn_sq + qe_sq)
    dbf['Q_dir'] = adcp_df.groupby(level=0).apply(mean_Vel_Dir_TN)
    if save:
        # Save DF in h5 format
        filename = "%s%s_%s.h5" % (FLUXES_PATH, filename, method)
        dbf.to_hdf(filename, key="df", mode="w")
        print(dbf.Q.max())
        print(dbf.Q.min())
        print("------")
    else:
        filename = "%s_%s" % (filename, method)
        plotter.plot_flux_windrose(dbf, filename)
