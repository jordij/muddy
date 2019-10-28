import numpy as np
from tools import encoder, plotter
from adcp import Aquadopp, RDI, Signature1000
from windrose import plot_windrose

FLUXES_PATH = "./data/fluxes/"
DZ = 0.1

plotter.set_font_sizes(big=False)


def calc_flux(dfl, dbf, adcp, method="average"):
    if method == "average":
        if dfl:  # 1/h * SSC(avg) in KG
            dbf.df_avg['C'] = ((dbf.df_avg.ssc + dfl.df_avg.ssc)/2) * (1/dbf.df_avg['depth_00'])
        else:  # 1/h * SSC
            dbf.df_avg['C'] = (dbf.df_avg.ssc) * (1/dbf.df_avg['depth_00'])
        # Q for N/S and E/W components
        dbf.df_avg['Q_N_TN'] = adcp.df.Vel_N_TN.groupby(level=0).sum() * DZ
        dbf.df_avg['Q_E_TN'] = adcp.df.Vel_E_TN.groupby(level=0).sum() * DZ
    else:
        dbf.df_avg['C'] = dbf.df_avg.ssc
        # Q for N/S and E/W components
        adcp_df = adcp.df.loc[pd.IndexSlice[:, adcp.HEIGHTS[0:2]], :]
        dbf.df_avg['Q_N_TN'] = adcp_df.Vel_N_TN.groupby(level=0).mean()
        dbf.df_avg['Q_E_TN'] = adcp_df.Vel_E_TN.groupby(level=0).mean()
    dbf.df_avg['QN'] = dbf.df_avg['C'] * dbf.df_avg['Q_N_TN']
    dbf.df_avg['QE'] = dbf.df_avg['C'] * dbf.df_avg['Q_E_TN']
    # U and V in average
    dbf.df_avg['U_avg'] = adcp.df.Vel_N_TN.groupby(level=0).mean()
    dbf.df_avg['V_avg'] = adcp.df.Vel_E_TN.groupby(level=0).mean()
    # Total Q and direction (degrees)
    dbf.df_avg['Q'] = np.sqrt(np.power(dbf.df_avg['QN'].astype(np.float32), 2) + np.power(dbf.df_avg['QE'].astype(np.float32), 2))
    dbf.df_avg['Qdir'] = np.degrees(np.arctan2(dbf.df_avg['U_avg'], dbf.df_avg['V_avg']))
    dbf.df_avg['Qdir'] = dbf.df_avg.apply(
        lambda r: r.Qdir + 360 if r.Qdir < 0 else r.Qdir, axis=1)
    print("MAX Q: " + str(dbf.df_avg['Q'].max()))
    print("MIN Q: " + str(dbf.df_avg['Q'].min()))
    # Save DF in h5 format
    dbf.df_avg.to_hdf("%s%s.h5" % (FLUXES_PATH, dbf.file), key="df", mode="w")
    # Plot flux rose
    ax = plot_windrose(dbf.df_avg, var_name="Q", direction_name="Qdir", kind='bar',
                       bins=np.arange(0, 100, 10), normed=True, opening=0.8)
    ax.set_yticks([])
    legend = ax.set_legend(
        bbox_to_anchor=(-0.25, 1),
        title="Q [mg/m/s]",
        loc='upper left')
    labels = [
        u"0 ≤ Q < 10",
        u"10 ≤ Q < 20",
        u"20 ≤ Q < 30",
        u"30 ≤ Q < 40",
        u"40 ≤ Q < 50",
        u"50 ≤ Q < 60",
        u"60 ≤ Q < 70",
        u"70 ≤ Q < 80",
        u"80 ≤ Q < 90",
        u"Q ≥ 90"]
    for i, l in enumerate(labels):
        legend.get_texts()[i].set_text(l)


adcps = [Aquadopp(1), Aquadopp(2), Aquadopp(3), Signature1000(4), RDI(5)]
i = 0
for dbf in encoder.create_devices_by_type("bedframe", "h5"):
    dfl = None
    if dbf.site != "S3":  # no floater
        dfl = encoder.create_device(dbf.site, "floater", "h5")
    adcp = adcps[i]
    calc_flux(dfl, dbf, adcp, method="bedframe")
    i += 1
