import fire
import logging

from constants import SITES, INST_TYPES, EVENT_DATES
from tools import plotter, encoder, structure, stats, station
import maps


class Muddy(object):
    """" Main Fire class """

    def plot_OBS_calibration(self):
        """ Generate OBS calibration plots """
        plotter.plot_obs_calibration()

    def daily_plots(self, origin="h5", site="all", dtype="floater"):
        """ Generate daily plots """
        if isinstance(origin, str):
            if origin not in ["h5", "rsk"]:
                raise ValueError("Origin 'h5' or 'rsk' value expected.")
        else:
            raise TypeError("Origin 'h5' or 'rsk' value expected.")
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if dtype not in INST_TYPES:
            raise ValueError("Type floater or bedframe expected.")

        if site != "all":  # just one instrument
            d = encoder.create_device(site, dtype, origin)
            d.plot_days()
        else:
            for t in INST_TYPES:  # all instruments
                for d in encoder.create_devices_by_type(t, origin):
                    d.plot_days()

    def avg_plots(self, site="all", dtype="floater"):
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if dtype not in INST_TYPES:
            raise ValueError("Type floater or bedframe expected.")

        if site != "all":  # just one instrument
            d = encoder.create_device(site, dtype, "h5")
            d.plot_avg()
        else:
            for t in INST_TYPES:  # all instruments
                for d in encoder.create_devices_by_type(t, "h5"):
                    d.plot_avg()

    def ssc_u_plots(self, site="all", dtype="bedframe"):
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if dtype not in INST_TYPES:
            raise ValueError("Type floater or bedframe expected.")
        if site != "all":  # just one instrument
            d = encoder.create_device(site, dtype, "h5")
            # if floater lets grab wave orbital velocity from bedframe
            if dtype == "floater":
                dbf = encoder.create_device(site, "bedframe", "h5")
                d.df_avg["u"] = dbf.df_avg["u"]
            d.plot_ssc_u()
        else:
            for t in INST_TYPES:  # all instruments
                for d in encoder.create_devices_by_type(t, "h5"):
                    if t == "floater":
                        dbf = encoder.create_device(d.site, "bedframe", "h5")
                        d.df_avg["u"] = dbf.df_avg["u"]
                    d.plot_ssc_u()

    def ssc_u_h_plots(self, site="all"):
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one instrument
            dbf = encoder.create_device(site, "bedframe", "h5")
            if site != "S3":  # no floater
                dfl = encoder.create_device(site, "floater", "h5")
                dbf.plot_ssc_u_h(dfl.df_avg)
            else:
                dbf.plot_ssc_u_h(None)
        else:
            # all bedframes
            for dbf in encoder.create_devices_by_type("bedframe", "h5"):
                if dbf.site != "S3":  # no floater
                    dfl = encoder.create_device(dbf.site, "floater", "h5")
                    dbf.plot_ssc_u_h(dfl.df_avg)
                else:
                    dbf.plot_ssc_u_h(None)

    def ssc_u_h_weekly_plots(self, site="all"):
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one instrument
            dbf = encoder.create_device(site, "bedframe", "h5")
            if site != "S3":
                dfl = encoder.create_device(site, "floater", "h5")
                dbf.plot_ssc_u_h_weekly(dfl.df_avg)
            else:  # no floater at site 3
                dbf.plot_ssc_u_h_weekly()
        else:
            # all bedframes
            for dbf in encoder.create_devices_by_type("bedframe", "h5"):
                if dbf.site != "S3":  # no floater
                    dfl = encoder.create_device(dbf.site, "floater", "h5")
                    dbf.plot_ssc_u_h_weekly(dfl.df_avg)
                else:
                    dbf.plot_ssc_u_h_weekly()

    def ssc_series_plot(self, dtype="bedframe"):
        if dtype not in INST_TYPES:
            raise ValueError("Type floater or bedframe expected.")
        devs = encoder.create_devices_by_type(dtype, "h5")
        plotter.plot_ssc_series(devs)

    def ssc_heatmap_plot(self, dtype="bedframe", event=False):
        if dtype not in INST_TYPES:
            raise ValueError("Type floater or bedframe expected.")
        devs = encoder.create_devices_by_type(dtype, "h5")
        if dtype == "bedframe":  # swap 3 and 4
            devs[2], devs[3] = devs[3], devs[2]
        if event:
            plotter.plot_ssc_heatmap(
                devs,
                start=EVENT_DATES["start"],
                end=EVENT_DATES["end"])
        else:
            plotter.plot_ssc_heatmap(devs)

    def series_event(self, dtype="bedframe"):
        start = EVENT_DATES["start"]
        end = EVENT_DATES["end"]
        otitle = "Event from %s to %s" % (start, end)
        dfrain = station.get_rainfall(start=start, end=end)
        dfrivers = station.get_rivers(start=start, end=end)
        dfpress = station.get_pressure(start=start, end=end)
        dfwind = station.get_wind(start=start, end=end)
        devs = encoder.create_devices_by_type(dtype, "h5")
        for d in devs:
            title = "%s - %s" % (otitle, d.site)
            df = d.df_avg[(d.df_avg.index >= start) & (d.df_avg.index < end)]
            if d.site != "S3":  # no floater
                dfl = encoder.create_device(d.site, "floater", "h5").df_avg
                dfl = dfl[(dfl.index >= start) & (dfl.index < end)]
            else:
                dfl = None
            plotter.plot_event(title, dfrain, dfrivers, dfpress, dfwind, df, dfl)

    def series_ssc_event(self, dtype="bedframe"):
        # SSC series
        start = EVENT_DATES["start"]
        end = EVENT_DATES["end"]
        title = "%s Event from %s to %s" % (dtype, start, end)
        devs = encoder.create_devices_by_type(dtype, "h5")
        for d in devs:
            d.df_avg = d.df_avg[(d.df_avg.index >= start) & (d.df_avg.index < end)]
        plotter.plot_event_ssc_series(devs, title)

    def stats(self):
        stats.basic_stats().to_csv('./data/stats.csv')

    def map_plots(self):
        maps.plot_transect()
        maps.plot_sites()
        maps.plot_bathymetry()

    def wind_plots(self):
        station.plot_wind()

    def rain_plot(self):
        station.plot_rain()

    def river_plot(self):
        station.plot_river_flows()

    def RSKtoH5(self, site="all", dtype="floater"):
        """ Store RSK data in h5 """
        if site not in SITES + ["all"]:
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one site (1 to 5)
            d = encoder.create_device(site, dtype, "rsk")
            d.save_H5(avg=False)
        else:
            for t in INST_TYPES:  # all instruments
                for d in encoder.create_devices_by_type(t, "rsk"):
                    d.save_H5(avg=False)

    def create_struct(self):
        structure.create_structure()


if __name__ == "__main__":
    fire.Fire(Muddy)
    logging.shutdown()
