import gsw
import math
import matplotlib.pyplot as plt
import numpy as np
import peakutils
import pandas as pd
from scipy.constants import pi as PI
from scipy.constants import g as G
from scipy import fftpack, signal


class Burst(object):
    r"""
    Represents a RbR Concerto depth_00 burst

    Parameters
    ----------
    df : pandas.DataFrame
        Water depth [m]
        Salinity [PSU]
        Temperature [°C]
    t : array_like, pandas.DatetimeIndex
        time series [s]
    f : int
        Signal frequency [Hz]
    z : float
        elevation of instrument over seabed
    """

    def __init__(self, df, t, f, z):
        self.df = df
        self.df.dropna(subset=[
            'salinity_00',
            'temperature_00',
            'seapressure_00'], inplace=True)
        self.t = t
        self.f = f
        self.rate = 1/f
        self.sr = len(self.df)
        self.ts = (df.index[-1] - df.index[0]).seconds
        self.z = z
        self._calc_density()
        self._calc_hydrostatic_depth()
        # other vars
        self.pp = None
        self._calc_T()
        self._calc_L()
        self._calc_K()
        self._calc_H()
        self._calc_U()

    def _calc_density(self):
        """
        Calculates density from Sal, Temp, Pressure.

        http://www.teos-10.org/pubs/gsw/html/gsw_rho_t_exact.html
        """
        self.df['density'] = self.df.apply(
            lambda r:  gsw.density.rho(
                r.salinity_00,
                r.temperature_00,
                r.seapressure_00),
            axis=1)

    def _calc_hydrostatic_depth(self):
        """
        Calculates density from Sal, Temp, Pressure.

        Math: h(t) = ((p(t) - pa)/ dens * G) + zp
        Note: pressure in Pascals (1dbar = 10000 P)
        """
        density_mean = self.df.density.mean()
        self.df['hydro_depth'] = self.df.apply(
            lambda r: ((r.seapressure_00*10000) / (density_mean * G)) + self.z,
            axis=1)
        self.df['hydro_depth_dt'] = signal.detrend(
                                        self.df.hydro_depth,
                                        type="linear")

    def _calc_L(self):
        """
        Iteratively calculates lambda from the dispersion relation.

        Math: lambda = (G / 2*PI) * T^2 * tanh(2*PI*h/lambda)
        """
        if self.pp:
            print("Mean period in peaks distance (0 - %s) is: %.2f" %
                  (str(self.sr), round(self.pp, 2)))
        # print("T: %.2f [s]" % round(self.T, 2))
        hd_mean = self.df.hydro_depth.mean()
        hd_sd = self.df.hydro_depth.std()
        # print("Mean hydrostatic depth: %.2f [m]" % hd_mean)
        # print("SD hydrostatic depth: %.2f [m]" % hd_sd)
        # Starting from guess value (suits deep water waves better)
        self.L = (G/(2 * PI)) * (self.T ** 2)
        # print("Estimated L: %.2f" % round(self.L, 2))
        # Iterative process
        err_tol = 1
        while err_tol > 1e-6:
            lb = (G / (2 * PI)) * (self.T ** 2) * np.tanh(2 * PI * (hd_mean / self.L))
            err_tol = np.abs(lb - self.L)
            self.L = lb
        # print("Converged L: %.2f" % round(self.L, 2))

    def _calc_K(self):
        """
        Calculate K-wave number

        Math: K = (2*PI) / lambda
        """
        self.K = round((2 * PI) / self.L, 2)
        # print("K wave number: %.2f" % self.K)

    def _calc_H(self):
        """
        Calculates significant wave height H

        Math: H = 4hSD * (cosh(k*h)/cosh[z* + h])
        """
        hd_sd = self.df.hydro_depth.std()
        hd_mean = self.df.hydro_depth.mean()
        self.H = 4 * hd_sd * ((np.cosh(self.K * hd_mean) / np.cosh(self.K * (self.z + hd_mean))))
        # print("Sig. wave height: %f [m]" % self.H)

    def _calc_U(self):
        """
        Calculates significant orbital speed athe bed U
        """
        hd_sd = self.df.hydro_depth.std()
        hd_mean = self.df.hydro_depth.mean()
        n = (4 * PI * hd_sd * np.cosh(self.K * hd_mean))
        d = (self.T * np.cosh(self.K * (self.z + hd_mean)) * np.sinh(self.K * hd_mean))
        self.U = n / d
        # print("Significant orbital speed: %f [m/s]" % self.U)

    def _calc_T(self):
        """ Method to be implemented in each subclass """
        raise NotImplementedError("Burst must define a method to calculate period T")

    def __str__(self):
        return ("Burst %s to %s") % (self.t[0], self.t[-1])

    def unicode(self):
        return self.__str__()

    def get_K(self):
        return self.K

    def get_lambda(self):
        return self.L

    def get_U(self):
        return self.U

    def get_T(self):
        return self.T

    def get_H(self):
        return self.H

    def get_UTH(self):
        return (self.U, self.T, self.H)

    def plot_freqs(self):
        """ Plot frequencies method to be implemented in each subclass """
        raise NotImplementedError("Burst must define a plot freqs method")

    def plot_peaks(self):
        """
        Plot signal peaks resulting from peakutils peak finder.

        Note: only works if method is 'peaks' when defining Burst
        """
        hd_mean = self.hydro_depth.mean()
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        nrow_series = pd.Series(np.arange(1, self.sr + 1), name='nrow')
        ax.plot(nrow_series, self.df.hydro_depth, marker=".", color="blue")
        ax.plot(self.peaks, self.df.hydro_depth[self.peaks], "x", color="r")
        ax.hlines(hd_mean, xmin=0, xmax=self.sr, linestyles="--", color="red")
        fig.show()


class BurstFourier(Burst):

    def _calc_T(self):
        """
        Apply scipy.fftpack.fft Fast Fourier Transform to signal
        self.df.hydro_depth_dt

        Result stored in self.T [s]
        """
        self.s_fft = fftpack.fft(self.df.hydro_depth_dt*signal.hann(self.sr))
        self.pwr = np.abs(self.s_fft)
        self.s_freq = fftpack.fftfreq(self.sr, d=self.rate)

        # Find the peak frequency, focus on only the positive frequencies
        self.freqs = self.s_freq[self.s_freq > 0]
        idx = np.argmax(np.abs(self.s_fft))
        self.pf = self.freqs[idx]  # peak freq
        self.ppwr = self.pwr[idx]  # peak power

        # Find the period T [s]
        # self.pp = 2*PI/self.pf  # peak period is 2*PI/peakfreq
        # self.T = (self.pp / self.sr) * self.ts  # in seconds
        # self.T = self.rate/self.pf
        self.T = 1/self.pf

    def plot_freqs(self):
        """
        Plot signal frequencies resulting from Fast Fourier Transform.
        """
        fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(12, 6))
        ax0.plot(self.t, self.df.depth_00, color="green", label="Depth")
        ax0.plot(self.t, self.df.hydro_depth, color="blue", label="Hydrostatic depth")
        ax0.set_xlabel('Date')
        ax0.set_ylabel('Depth [m]')
        ax1.plot(self.t, self.df.hydro_depth_dt, color="blue", label="Hydrostatic depth (detrended)")
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Depth [m]')
        # ax1.plot(self.s_freq, self.pwr)
        # ax1.set_xlabel('Frequency [Hz]')

        # plot the peak frequency
        ax2.plot(self.freqs, self.pwr[:len(self.freqs)], label="Welch", color="blue")
        ax2.set_xlabel('Frequency [Hz]')
        ax2.set_ylabel('Frequency Spectrum Magnitude')

        # inverse FFT
        # remove higher freqs than Peak Freq
        fft_bis = self.s_fft.copy()
        fft_bis[np.abs(self.s_freq) > self.pf] = 0
        ifft = np.real(fftpack.ifft(fft_bis))
        ax1.plot(self.t, ifft, color="red", label='Inverse FFT')
        ax0.legend()
        ax1.legend()
        ax2.legend()


class BurstWelch(Burst):

    def _calc_T(self):
        """
        Apply scipy.signal.welch to signal self.df.hydro_depth_dt

        Result stored in self.T [s]
        """
        self.freqs, self.pwr = signal.welch(
            self.df.hydro_depth_dt,
            self.f,
            nperseg=int(math.ceil(self.sr/4 + self.sr/8)))  # 768 if sr is 2048 (full burst)
            # noverlap=30,
            # average="median",
            # detrend="constant")
        idx = np.argmax(np.abs(self.pwr))
        self.pf = self.freqs[idx]  # peak freq
        self.ppwr = self.pwr[idx]  # peak power
        self.T = 1/self.pf

    def plot_freqs(self):
        """
        Plot signal frequencies resulting from Welch.
        """
        fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(12, 6))
        ax0.plot(self.t, self.df.depth_00, color="green", label="Depth")
        ax0.plot(self.t, self.df.hydro_depth, color="blue", label="Hydrostatic depth")
        ax0.set_xlabel('Date')
        ax0.set_ylabel('Depth [m]')
        ax1.plot(self.t, self.df.hydro_depth_dt, color="blue", label="Hydrostatic depth (detrended)")
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Depth [m]')
        # plot the peak frequency
        ax2.plot(self.freqs, self.pwr[:len(self.freqs)], label="Welch", color="blue")
        ax2.set_xlabel('Frequency [Hz]')
        ax2.set_ylabel('Power Spectral Density [m^2/Hz]')
        print("Peak frequency is: %.2f" % round(self.pf, 2))
        print("Power [] at peak frequency is: %.2f" % round(self.ppwr, 2))
        ax2.plot(
            self.freqs,
            signal.savgol_filter(self.pwr, window_length=25, polyorder=10, mode='interp')[:len(self.freqs)],
            label="Savitzky-Golay",
            color="green")
        ax2.plot(
            self.freqs,
            signal.wiener(self.pwr, mysize=25)[:len(self.freqs)],
            label="Wiener",
            color="red")
        ax0.legend()
        ax1.legend()
        ax2.legend()


class BurstPeaks(Burst):

    def _calc_T(self):
        """
        Apply peakutils.indexes to find relevant peaks in
        self.df.hydro_depth and average periods

        Result stored in self.T [s]
        """
        self.peaks = peakutils.indexes(
                        self.df.hydro_depth,
                        min_dist=10,
                        thres=self.df.hydro_depth.mean(),
                        thres_abs=True)
        periods = np.diff(self.peaks)  # difference between peaks
        mean_period = round(sum(periods)/len(periods), 2)
        self.T = (mean_period / self.sr) * (self.t[-1] - self.t[0]).seconds

    def plot_freqs(self):
        return None
