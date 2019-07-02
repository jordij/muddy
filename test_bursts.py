from tools import encoder


device = encoder.create_device("S5", "bedframe", "h5")
burst = device.get_burst(start="2017-05-12 15:00", end="2017-05-12 15:09", method="fourier")
burst.plot_frequencies()

burst = device.get_burst(start="2017-05-12 15:00", end="2017-05-12 15:09", method="peaks")
burst.plot_peaks()
