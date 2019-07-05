from tools import encoder


device = encoder.create_device("S2", "bedframe", "h5")
burst_0 = device.get_burst(start="2017-05-12 18:10", end="2017-05-12 18:20", method="fourier")
burst_0.plot_frequencies()

device = encoder.create_device("S5", "bedframe", "h5")
burst_1 = device.get_burst(start="2017-05-12 18:10", end="2017-05-12 18:20", method="fourier")
burst_1.plot_frequencies()


# burst = device.get_burst(start="2017-05-12 15:00", end="2017-05-12 15:09", method="peaks")
# burst.plot_peaks()
