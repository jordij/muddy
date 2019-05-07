# -*- coding: utf-8 -*-
import os

path = os.getcwd()

sites = ["S1", "S2", "S3", "S4", "S5"]
concertos = ["floater", "bedframe"]
variables = [
    "temperature_00",
    "pressuretemperature_00",
    "conductivitycelltemperature_00",
    "turbidity_00",
    "pressure_00",
    "conductivity_00",
    "all"
]

print("The current working directory is %s" % path)

file_path = "./output"
directory = os.path.dirname(file_path)
if not os.path.exists(directory):
    os.makedirs(directory)

for site in sites:
    site_folder = os.path.join(file_path, site)
    if not os.path.exists(site_folder):
        os.makedirs(site_folder)
    for concerto in concertos:
        conc_folder = os.path.join(file_path, site, concerto)
        if not os.path.exists(conc_folder):
            os.makedirs(conc_folder)
        for variable in variables:
            var_folder = os.path.join(file_path, site, concerto, variable)
            if not os.path.exists(var_folder):
                os.makedirs(var_folder)
