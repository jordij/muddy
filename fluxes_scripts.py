from adcp import Aquadopp, RDI, Signature1000
from fluxes import calc_flux
import pandas as pd
from tools import encoder, plotter
from intervals import DATA_INTERVALS, FLUXES_INTERVALS


def calc_fluxes(adcps):
    for adcp in adcps:
        site = adcp.get_site()
        dbf = encoder.create_device(site, "bedframe", "h5")
        dfl = None
        if site != "S3":  # no floater
            dfl = encoder.create_device(dbf.site, "floater", "h5")
        calc_flux(
            dfl.df_avg if dfl else None,
            dbf.df_avg,
            adcp.df,
            site,
            adcp.HEIGHTS[0:2],
            save=False,
            method="bedframe")


def plot_fluxes():
    for s in ["S1", "S2", "S3", "S4", "S5"]:
        df = encoder.get_flux_df(s)
        plotter.plot_timeseries_flux(df)


def net_fluxes():
    total_fluxes = []
    for s in ["S1", "S2", "S3", "S4", "S5"]:
        df = encoder.get_flux_df(s)
        fluxes = pd.DataFrame(columns=["Date", "Q", "Site"])
        intervals = DATA_INTERVALS['%s Bedframe' % s]
        if not intervals:
            intervals = FLUXES_INTERVALS['%s Bedframe' % s]
        for i in intervals:
            dfinterval = df[i[0]:i[1]]
            q_neg = dfinterval[(dfinterval.Q_dir < 67) | (dfinterval.Q_dir > 247)] * 600
            q_pos = dfinterval[(dfinterval.Q_dir >= 67) & (dfinterval.Q_dir <= 247)] * 600
            q_net = q_pos["Q"].abs().sum() - q_neg["Q"].abs().sum()
            fluxes = fluxes.append({
                "Date": dfinterval.index[0],
                "Q": q_net,
                "Site": s}, ignore_index=True)
        fluxes = fluxes.set_index("Date")
        total_fluxes.append(fluxes)
    plotter.plot_total_fluxes(total_fluxes)


def total_fluxes():
    total = 0
    for s in ["S1", "S2", "S3", "S4", "S5"]:
        df = encoder.get_flux_df(s)
        fluxes = []
        # q_neg = df[(df.Q_dir < 90) | (df.Q_dir > 270)].Q.sum()
        # q_pos = df[(df.Q_dir >= 90) & (df.Q_dir <= 270)].Q.sum()
        # q_net = q_pos - q_neg
        q_neg = df[(df.Q_dir < 67) | (df.Q_dir > 247)]*600
        q_pos = df[(df.Q_dir >= 67) & (df.Q_dir <= 247)]*600
        q_net = q_pos["Q"].abs().sum() - q_neg["Q"].abs().sum()
        print("%s SITE NET FLUX IS: %d" % (s, q_net))
        total = total + q_net
    print("TOTAL NET FLUX IS: %d" % total)


def total_horizontal_fluxes():
    total = 0
    for s in ["S1", "S2", "S3", "S4", "S5"]:
        df = encoder.get_flux_df(s)
        fluxes = []
        q_neg = df[(df.V_avg < 0)]*600
        q_pos = df[(df.V_avg > 0)]*600
        q_neg = q_neg.Q.sum()
        q_pos = q_pos.Q.sum()
        print("Total towards W: %f" % q_neg)
        print("Total towards E: %f" % q_pos)
        q_net = q_pos + q_neg
        print("%s SITE NET FLUX IS: %d" % (s, q_net))
        total = total + q_net
    print("TOTAL NET FLUX IS: %d" % total)


def plot_intervals(site, interval):
    df = encoder.get_flux_df(s)
