from tools import encoder


################################
# Episode for Site 1 - 6th June
################################

dates = [
#     "2017-06-05 13:50:00",
     "2017-05-18 14:00:00",
     "2017-05-18 14:10:00",
#     "2017-06-05 14:20:00"
 ]

device = encoder.create_device("S5", "bedframe", "h5")
for i, d in enumerate(dates):
    if i < len(dates) - 1:
        burst = device.get_burst(start=d, end=dates[i + 1], method="welch")
        burst.plot_freqs()
        print(str(burst))
        print("U [cm/s], T [s], H [m] : %s" % str(burst.get_UTH()))

################################
# Episode for Site 1 - 17th May
################################

# dates = [
#     "2017-05-17 23:20:00",
#     "2017-05-17 23:30:00",
#     "2017-05-17 23:40:00",
#     "2017-05-17 23:50:00"
# ]
# for i, d in enumerate(dates):
#     if i < len(dates) - 1:
#         burst = device.get_burst(start=d, end=dates[i + 1], method="welch")
#         burst.plot_freqs()
#         print(str(burst))
#         print("U [cm/s], T [s], H [m] : %s" % str(burst.get_UTH()))

################################
# Episode for Site 2 - 13th May
################################

#device = encoder.create_device("S2", "bedframe", "h5")
#
#dates = [
#    "2017-05-13 06:00:00",
#    "2017-05-13 06:10:00",
#    "2017-05-13 06:20:00",
#    "2017-05-13 06:30:00"
#]
#for i, d in enumerate(dates):
#    if i < len(dates) - 1:
#        burst = device.get_burst(start=d, end=dates[i + 1], method="fourier")
#        burst.plot_freqs()
#        print(str(burst))
#        print("U: %.2f [cm/s], T: %.2f [s], H: %.2f [m]" % burst.get_UTH())


# device = encoder.create_device("S1", "bedframe", "h5")
# burst_1 = device.get_burst(start="2017-05-12 18:10", end="2017-05-12 18:20", method="fourier")
# burst_1.plot_freqs()

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
