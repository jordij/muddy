import os

from constants import OUTPUT_PATH, SITES, INST_TYPES, AVG_FOLDER


def create_structure():
    path = os.getcwd()
    print("The current working directory is %s" % path)
    directory = os.path.dirname(OUTPUT_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        print("%s already exists" % OUTPUT_PATH)
    for site in SITES:
        site_folder = os.path.join(OUTPUT_PATH, site)
        if not os.path.exists(site_folder):
            os.makedirs(site_folder)
        else:
            print("%s already exists" % site)
        for inst in INST_TYPES:
            conc_folder = os.path.join(OUTPUT_PATH, site, inst)
            if not os.path.exists(conc_folder):
                os.makedirs(conc_folder)
            else:
                print("%s %s already exists" % (site, inst))
            conc_folder = os.path.join(OUTPUT_PATH, site, "adcp")
            if not os.path.exists(conc_folder):
                os.makedirs(conc_folder)
            else:
                print("%s %s already exists" % (site, "adcp"))
            conc_folder = os.path.join(OUTPUT_PATH, site, inst, AVG_FOLDER)
            if not os.path.exists(conc_folder):
                os.makedirs(conc_folder)
            else:
                print("%s %s already exists" % (site, inst))
