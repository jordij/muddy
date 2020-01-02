import pandas as pd
from tools import encoder, plotter


def plot_ssc_vs_u(concertos):
    df_tidal = pd.DataFrame()
    frames = [c.get_intervals_df() for c in concertos]
    df = pd.concat(frames, sort=True)
    plotter.plot_ssc_vs_u(df)


def tidal_stats(concertos):
    for c in concertos:
        print(c.site)
        print(c.get_intervals_df().groupby(["Tide"]).ssc.mean())
        print(c.get_intervals_df().groupby(["Tide"]).ssc.min())
        print(c.get_intervals_df().groupby(["Tide"]).ssc.max())
