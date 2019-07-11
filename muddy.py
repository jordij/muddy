import fire

from constants import SITES, INST_TYPES
from tools import plotter, encoder, structure
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

    def ssc_u_plots(self, site="all"):
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one instrument
            d = encoder.create_device(site, "bedframe", "h5")
            d.plot_ssc_u()
        else:
            # all bedframes
            for d in encoder.create_devices_by_type("bedframe", "h5"):
                d.plot_ssc_u()

    def ssc_u_h_plots(self, site="all"):
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one instrument
            d = encoder.create_device(site, "bedframe", "h5")
            d.plot_ssc_u_h()
        else:
            # all bedframes
            for d in encoder.create_devices_by_type("bedframe", "h5"):
                d.plot_ssc_u_h()

    def map_plots(self):
        maps.plot_transect()
        maps.plot_sites()
        maps.plot_bathymetry()

    def RSKtoH5(self, site="all", dtype="floater"):
        """ Store RSK data in h5 """
        if site not in SITES + ["all"]:
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one site (1 to 5)
            d = encoder.create_device(site, dtype, "rsk")
            d.save_H5(avg=False)
        else:
            for t in INST_TYPES:  # all instruments
                for d in encoder.create_devices_by_type(t, "h5"):
                    d.save_H5(avg=False)

    def create_struct(self):
        structure.create_structure()


if __name__ == "__main__":
    fire.Fire(Muddy)
