import matplotlib.pyplot as plt
import numpy as np
import peakutils
import pandas as pd
from scipy.constants import pi as PI
from scipy.constants import g as G
from scipy import fftpack


class Burst(object):
    r"""
    Represents a RbR Concerto depth_00 burst

    Parameters
    ----------
    d : pandas.Series
        Water depth [m]
    t : array_like, pandas.DatetimeIndex
        time series [s]
    f : int
        Signal d frequency [Hz]
    ts : float
         time series total duration [s]
    method : string
        'fourier' or 'peaks'
    """

    def __init__(self, d, t, f, ts, method='fourier'):
        self.d = d
        self.t = t
        self.f = f
        self.rate = 1/f
        self.sr = len(self.d)
        self.ts = ts  # (dfburst.index[-1] - dfburst.index[0]).seconds
        if method not in ["fourier", "peaks"]:
            raise ValueError("Unknown method")
        self.d_mean = self.d.mean()  # store original water depth mean

        # other vars
        self.pp = None

        if method == 'fourier':
            # Check depth is 0-aligned
            if round(self.d.mean(), 2) != 0:
                self.d = self.d - self.d.mean()
            self._apply_fft()
        else:
            self._apply_avg_peak()

        self.set_lambda()
        self.set_K()

    def _apply_fft(self):
        """
            Apply scipy.fftpack.fft Fast Fourier Transform to signal self.d

            Result stored in self.T [s]
        """
        s_fft = fftpack.fft(self.d)
        self.pwr = np.abs(s_fft)
        self.s_freq = fftpack.fftfreq(self.sr, d=self.rate)

        # Find the peak frequency, focus on only the positive frequencies
        self.freqs = self.s_freq[1:self.sr//2]  # filter freqs <=0
        idx = np.argmax(np.abs(s_fft))
        self.pf = self.freqs[idx]  # peak freq
        self.ppwr = self.pwr[idx]  # peak power

        # Find the period T [s]
        self.pp = 2*PI/self.pf  # peak period is 2*PI/peakfreq
        self.T = (self.pp / self.sr) * self.ts  # in seconds

    def _apply_avg_peak(self):
        """
            Apply peakutils.indexes to find relevant peaks in self.d, then average periods

            Result stored in self.T [s]
        """
        self.peaks = peakutils.indexes(self.d, min_dist=10, thres=self.d_mean, thres_abs=True)
        periods = np.diff(self.peaks)  # difference between peaks
        mean_period = round(sum(periods)/len(periods), 2)
        period_secs = (mean_period / self.sr) * (self.t[-1] - self.t[0]).seconds
        self.T = period_secs

    def set_lambda(self):
        """
        Iteratively calculates lambda from the dispersion relation.

        Math: lambda = (G / 2*PI) * T^2 * tanh(2*PI*h/lambda)
        """
        if self.pp:
            print("Mean period in peaks distance (0 - %s) is: %.2f" %
                  (str(self.sr), round(self.pp, 2)))
        print("T in seconds is: %.2f" % round(self.T, 2))
        print("Mean water depth in m is %.2f" % self.d_mean)
        # Starting from guess value (suits deep water waves better)
        self._lambda = (G/(2 * PI)) * (self.T ** 2)
        print("Estimated lambda at the beginning is: %.2f" % round(self._lambda, 2))
        # Iterative process
        err_tol = 1
        while err_tol > 1e-6:
            lb = (G / (2 * PI)) * (self.T ** 2) * np.tanh(2 * PI * (self.d_mean / self._lambda))
            err_tol = np.abs(lb - self._lambda)
            self._lambda = lb
        print("Converged value of lambda: %.2f" % round(self._lambda, 2))

    def set_K(self):
        """
            Calculate K-wave number

            Math: K = (2*PI) / lambda
        """
        self.K = round((2 * PI) / self._lambda, 2)
        print("K wave number is %.2f" % self.K)

    def get_K(self):
        return self.K

    def get_lambda(self):
        return self._lambda

    def plot_frequencies(self):
        """
        Plot signal frequencies resulting from Fast Fourier Transform.

        Note: only works if method is 'fourier' when defining Burst
        """
        fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(12, 6))
        ax0.plot(self.t, self.d, color="blue", label="Signal")
        ax0.set_xlabel('Date')
        ax0.set_ylabel('Depth (m)')
        ax1.plot(self.s_freq, self.pwr)
        ax1.set_xlabel('Frequency / Hz')

        # plot the peak frequency
        ax2.plot(self.freqs, self.pwr[:len(self.freqs)])
        ax2.set_xlabel('Frequency / Hz')
        print("Peak frequency is: %.2f" % round(self.pf, 2))
        print("Power (db?) at peak frequency is: %.2f" % round(self.ppwr, 2))
        # inverse FFT
        # remove higher freqs than Peak Freq
        # fft_bis = s_fft.copy()
        # fft_bis[np.abs(s_freq) > self.pf] = 0
        # ifft = np.real(fftpack.ifft(fft_bis))
        # ax0.plot(self.t, ifft, color="red", label='Inverse Fourier')
        # ax0.legend()

    def plot_peaks(self):
        """
            Plot signal peaks resulting from peakutils peak finder.

            Note: only works if method is 'peaks' when defining Burst
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        nrow_series = pd.Series(np.arange(1, self.sr + 1), name='nrow')
        ax.plot(nrow_series, self.d, marker=".", color="blue")
        ax.plot(self.peaks, self.d[self.peaks], "x", color="r")
        ax.hlines(self.d_mean, xmin=0, xmax=self.sr, linestyles="--", color="red")
        fig.show()
