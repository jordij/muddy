"""" Constant variables """

TIMEZONE = "Pacific/Auckland"

OUTPUT_PATH = "./plots/"

RAW_PATH = "D:/EE-FoT-May2017Expt/Concertos/RawData/"
PROCESSED_PATH = "./data/rsk/"
H5_PATH = "./data/hd5/"
AVG_FOLDER = "average"

BATHYMETRY_PATH = "./data/transect_bathymetry.csv"

INSTR_LOCS_PATH = "./data/Instrument_Locs.csv"
BASEMAP_IMG_PATH = "./data/lds-chart-nz-533-firth-of-thames-JPEG/chart-nz-" \
                    "533-firth-of-thames.jpg"
# transect
LONS = [175.416278, 175.445361, 175.445361, 175.4162781]
LATS = [-37.206863, -37.206863, -37.155814, -37.155814]

# sites distance in m
SITES_DISTANCES = [
    0.0,
    486.9258201722962,
    1507.2329501732236,
    2597.228501656257,
    6239.191158574506
]

# rsk variables
TURBIDITY = {"name": "Turbidity", "units": "NTU"}
DEPTH = {"name": "Depth", "units": "m"}
VARIABLES = {
    # Original variables
    "conductivity_00": {
        "name": "Conductivity", "units": "mS/cm"
    },
    "temperature_00": {
        "name": "Temperature", "units": "°C"
    },
    "pressuretemperature_00": {
        "name": "Pressure temperature", "units": "°C"
    },
    "conductivitycelltemperature_00": {
        "name": "Conductivity cell temperature", "units": "°C"
    },
    "turbidity_00": TURBIDITY,
    "pressure_00": {
        "name": "Pressure", "units": "dbar"
    },
    # derived variables
    "seapressure_00": {
        "name": "Sea Pressure", "units": "dbar"
    },
    "depth_00": DEPTH,
    "salinity_00": {
        "name": "Salinity", "units": "PSU"
    }
}

SITES = ["S1", "S2", "S3", "S4", "S5"]
INST_TYPES = ["floater", "bedframe"]

# devices per site
DEVICES = [
    # floaters
    {
        "name": "S1",
        "file": "066010_20170704_0850",
        "type": "floater",
        "freq": 6,  # hz
        "burst_samples": 1024,  # per burst
        "interval": 600  # between start of each burst
    },
    {
        "name": "S2",
        "file": "065761_20170702_1030",
        "type": "floater",
        "freq": 6,  # hz
        "burst_samples": 1024,  # per burst
        "interval": 600  # between start of each burst
    },
    {
        "name": "S4",
        "file": "065762_20170630_1524",
        "type": "floater",
        "freq": 6,  # hz
        "burst_samples": 1024,  # per burst
        "interval": 600  # between start of each burst
    },
    {
        "name": "S5",
        "file": "065760_20170702_1005",
        "type": "floater",
        "freq": 12,  # hz
        "burst_samples": 1024,  # per burst
        "interval": 600  # between start of each burst
    },
    # bedframes
    {
        "name": "S1",
        "file": "066011_20170703_1431",
        "type": "bedframe",
        "freq": 6,  # hz
        "burst_samples": 2048,  # per burst
        "interval": 600  # between start of each burst
    },
    {
        "name": "S2",
        "file": "065818_20170701_0947",
        "type": "bedframe",
        "freq": 6,  # hz
        "burst_samples": 2048,  # per burst
        "interval": 600  # between start of each burst
    },
    {
        "name": "S3",
        "file": "065819_20170701_0953",
        "type": "bedframe",
        "freq": 6,  # hz
        "burst_samples": 2048,  # per burst
        "interval": 600  # between start of each burst
    },
    {
        "name": "S4",
        "file": "065821_20170703_1419",
        "type": "bedframe",
        "freq": 6,  # hz
        "burst_samples": 2048,  # per burst
        "interval": 600  # between start of each burst
    },
    {
        "name": "S5",
        "file": "065820_20170704_0838",
        "type": "bedframe",
        "freq": 6,  # hz
        "burst_samples": 2048,  # per burst
        "interval": 600  # between start of each burst
    }
]


PLOT_VARS = {
    "x": ["depth_00", "salinity_00"],
    "y": ["turbidity_00", "sd_turb"]
}
