# -*- coding: utf-8 -*-
import os

from constants import OUTPUT_PATH, SITES, INST_TYPES


def create_structure():
    path = os.getcwd()
    print("The current working directory is %s" % path)
    directory = os.path.dirname(OUTPUT_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)
    for site in SITES:
        site_folder = os.path.join(OUTPUT_PATH, site)
        if not os.path.exists(site_folder):
            os.makedirs(site_folder)
        for inst in INST_TYPES:
            conc_folder = os.path.join(OUTPUT_PATH, site, inst)
            if not os.path.exists(conc_folder):
                os.makedirs(conc_folder)
