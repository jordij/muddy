import fire

from constants import DEVICES, SITES
from tools import plotter, encoder, structure
import maps


class Muddy(object):
    """" Main Fire class """

    def obs_plots(self, origin="h5"):
        """ Generate OBS calibration plots """
        if isinstance(origin, str):
            if origin not in ["h5", "rsk"]:
                raise ValueError("String 'hd' or 'rsk' value expected.")
        else:
            raise TypeError("String 'hd' or 'rsk' value expected.")
        plotter.plot_obs_calibration(origin)

    def daily_plots(self, origin="h5", site="all"):
        """ Generate daily plots """
        if isinstance(origin, str):
            if origin not in ["h5", "rsk"]:
                raise ValueError("String 'hd' or 'rsk' value expected.")
        else:
            raise TypeError("String 'hd' or 'rsk' value expected.")
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one site (1 to 5)
            site = encoder.get_device(site)
        plotter.plot_all_days(origin, site)

    def avg_plots(self, origin="h5", site="all"):
        if isinstance(origin, str):
            if origin not in ["h5", "rsk"]:
                raise ValueError("String 'h5' or 'rsk' value expected.")
        else:
            raise TypeError("String 'processed' or 'raw' value expected.")
        if site not in (SITES + ["all"]):
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one site (1 to 5)
            site = encoder.get_device(site)
        plotter.plot_all_avg(origin, site)

    def map_plots(self):
        maps.plot_transect()
        maps.plot_sites()
        maps.plot_bathymetry()

    def storeH5(self, origin="processed", site="all"):
        """ Store raw data in h5 to read/write heaps faster than .rsk"""
        if isinstance(origin, str):
            if origin not in ["processed", "raw"]:
                raise ValueError("String 'processed' or 'raw' value expected.")
        else:
            raise TypeError("String 'processed' or 'raw' value expected.")
        if site not in SITES + ["all"]:
            raise ValueError("String 'S(n)' n being 1 to 5 expected.")
        if site != "all":  # just one site (1 to 5)
            dsite = next(item for item in DEVICES if item["name"] == site)
            encoder.store_deviceH5(dsite, origin)
        else:
            for d in DEVICES:
                encoder.store_deviceH5(d, origin)

    def create_struct(self):
        structure.create_structure()


if __name__ == "__main__":
    fire.Fire(Muddy)
