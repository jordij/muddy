from tools import encoder


device = encoder.create_device("S1", "bedframe", "h5")
burst_0 = device.get_burst(start="2017-05-12 18:10", end="2017-05-12 18:20", method="welch")
burst_0.plot_freqs()

device = encoder.create_device("S1", "bedframe", "h5")
burst_1 = device.get_burst(start="2017-05-12 18:10", end="2017-05-12 18:20", method="fourier")
burst_1.plot_freqs()

# device = encoder.create_device("S2", "bedframe", "h5")
# burst_0 = device.get_burst(start="2017-05-12 18:10", end="2017-05-12 18:20", method="fourier")
# burst_0.plot_freqs()

# device = encoder.create_device("S2", "bedframe", "h5")
# burst_1 = device.get_burst(start="2017-05-13 18:10", end="2017-05-13 18:20", method="welch")
# burst_1.plot_freqs()

# device = encoder.create_device("S3", "bedframe", "h5")
# burst_2 = device.get_burst(start="2017-05-13 18:10", end="2017-05-13 18:20", method="welch")
# burst_2.plot_freqs()

# device = encoder.create_device("S4", "bedframe", "h5")
# burst_3 = device.get_burst(start="2017-05-13 18:10", end="2017-05-13 18:20", method="welch")
# burst_3.plot_freqs()

# device = encoder.create_device("S5", "bedframe", "h5")
# burst_4 = device.get_burst(start="2017-05-13 18:10", end="2017-05-13 18:20", method="welch")
# burst_4.plot_freqs()


# burst = device.get_burst(start="2017-05-12 15:00", end="2017-05-12 15:09", method="peaks")
# burst.plot_peaks()
