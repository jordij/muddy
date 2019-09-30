import matplotlib.pyplot as plt

from adcp import Aquadopp, RDI, Signature1000
from constants import CALM_EVENT_DATES


def plot_depths():
    s1 = Aquadopp(1)
    s2 = Aquadopp(2)
    s3 = Aquadopp(3)
    s4 = Signature1000(4)
    s5 = RDI(5)
    fig, ax = plt.subplots()
    for s in [s1, s2, s3, s4, s5]:
        df = s.wd[CALM_EVENT_DATES["start"]:CALM_EVENT_DATES["end"]]
        ax.plot(df.index, df["WaterDepth"], label=str(s))
        fig.legend()
