from constants import DEVICES, H5_PATH
import matplotlib.pyplot as plt
import peakutils
from peakutils.plot import plot as pplot
import numpy as np
from numpy import argmax
import pandas as pd
import scipy
from scipy.signal import find_peaks, find_peaks_cwt
from scipy.constants import pi as PI
from scipy.constants import g as G
from scipy import fftpack
from scipy.signal import blackmanharris, fftconvolve

from burst import Burst


dev = DEVICES[8]
datapath = "%s%s.h5" % (H5_PATH, dev["file"])
print("Using %s as a dataframe source for %s %s" %
      (datapath, dev["name"], dev["type"]))
df = pd.read_hdf(datapath, "df")
print(df.shape)
print("Any NaN values? -> %s" % str(df.isnull().T.any().T.sum()))

dfburst = df['2017-05-12 15:00':'2017-05-12 15:09']
ts = (dfburst.index[-1] - dfburst.index[0]).seconds

burst = Burst(dfburst.depth_00, dfburst.index, dev["freq"], ts, method='fourier')
burst.plot_frequencies()

burst = Burst(dfburst.depth_00, dfburst.index, dev["freq"], ts, method='peaks')
burst.plot_peaks()
