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


# start and end experiment dates, exactly 4 weeks - 28 days
# NZST
DATES = {
    "start": "2017-05-15 00:00:00",
    "end": "2017-06-12 00:00:00",
}
ADCP_DATES = {
    "start": "2017-05-15 00:00:00",
    "end": "2017-06-11 23:50:00",
}
# Storm event dates
EVENT_DATES = {
    "start": "2017-05-17 00:00:00",
    "end": "2017-05-20 00:00:00",
}
POSTER_DATES = {
    "start": "2017-05-17 17:00:00",
    "end": "2017-05-18 05:00:00",
}
# Calm dates
CALM_EVENT_DATES = {
    "start": "2017-06-11 00:00:00",
    "end": "2017-06-11 18:00:00",
}
DATES_FORMAT = "%Y-%m-%d %H:%M:%S"
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

MIN_DEPTH = 0.05  # in m, always >
MIN_TURB = 0  # in NTU, always >
Z_ELEVATION = 0.15  # 15cm - elevation above the seabed of pressure sensor

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
    },
    # from interpolating OBS calibration values
    "ssc": {
        "name": "SSC", "units": "mg/l"
    },
    "ssc_sd": {
        "name": "SSC Standard Dev.", "units": "mg/l"
    },
    "u": {
        "name": "Wave orbital velocity", "units": "cm/s"
    },
    "H": {
        "name": "Significant wave height", "units": "m"
    },
    "T": {
        "name": "Peak period", "units": "s"
    }
}

SITES = ["S1", "S2", "S3", "S4", "S5"]

INST_TYPES = ["floater", "bedframe"]

# devices per site
DEVICES = [
    # floaters
    {
        "site": "S1",
        "file": "066010_20170704_0850",
        "type": "floater",
        "freq": 6,  # Hz
        "burst_samples": 1024,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.05,  # m
        "ssc_saturated_value": 2115,  # del max values as instrument saturated
        "T": [
            0.365204377190083,
            175.693553881483,
            498.013240143255,
            668.288344684656,
            874.659566918661,
            1172.10145607251
        ],
        "SSC": [
            0,
            235,
            796,
            1045,
            1410,
            2115
        ]
    },
    {
        "site": "S2",
        "file": "065761_20170702_1030",
        "type": "floater",
        "freq": 6,  # Hz
        "burst_samples": 1024,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.05,  # m
        "T": [
            0.637296553243671,
            214.082930151096,
            631.304316669114,
            787.634857274657,
            981.484060137614,
            1128.06214798614
        ],
        "SSC": [
            0,
            235,
            796,
            1045,
            1410,
            2115
        ]
    },
    {
        "site": "S4",
        "file": "065762_20170630_1524",
        "type": "floater",
        "freq": 6,  # Hz
        "burst_samples": 1024,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.005,  # m
        "T": [
            0.626031610758164,
            191.844304522655,
            554.058101961811,
            723.246655121903,
            893.583789274031
        ],
        "SSC": [
            0,
            235,
            796,
            1045,
            1410
        ]
    },
    {
        "site": "S5",
        "file": "065760_20170702_1005",
        "type": "floater",
        "freq": 12,  # Hz
        "burst_samples": 1024,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.0,
        "T": [
            0.628385211292066,
            24.7638523241980,
            49.9693816165454,
            105.521706409818,
            207.961955184886,
            589.571061775594,
            752.960934219280,
            918.052001113798,
            1057.85550293406
        ],
        "SSC": [
            0,
            31.4,
            67,
            147,
            235,
            796,
            1045,
            1410,
            2115
        ]
    },
    # bedframes
    {
        "site": "S1",
        "file": "066011_20170703_1431",
        "type": "bedframe",
        "freq": 6,  # Hz
        "burst_samples": 2048,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.1,  # m
        "T": [  # OBS calibration
            0.478731970628837,
            41.6036219974082,
            280.468656161321,
            523.216026144310,
            658.794812959047,
            787.341499836078,
            895.559608175895,
            1009.07682239060,
            1093.01414122010,
            1175.40887018838,
            1252.51702952588,
            1298.01821619360,
            1359.66201728161,
            1391.79943829116,
            1412.76434035124,
            1438.40579523788,
            1439.24617204336
        ],
        "SSC": [
            0,
            71.7,
            482.5,
            902,
            1175,
            1385,
            1690,
            1950,
            2170,
            2485,
            2680,
            2960,
            3140,
            3405,
            3595,
            3775,
            4050
        ]
    },
    {
        "site": "S2",
        "file": "065818_20170701_0947",
        "type": "bedframe",
        "freq": 6,  # Hz
        "burst_samples": 2048,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.005,  # m
        "T": [  # OBS calibration
            0.484052564688328,
            41.2126669704134,
            285.016997248508,
            523.595929126400,
            665.501981447761,
            804.715472404538,
            923.946003029343,
            1008.22750734407,
            1120.86602942789,
            1205.79259266735,
            1278.04840886838,
            1337.62977721946,
            1385.40526203627,
            1418.82645948918,
            1433.65299247322,
            1471.84029993176,
            1470.45550976637
        ],
        "SSC": [
            0,
            71.7,
            482.5,
            902,
            1175,
            1385,
            1690,
            1950,
            2170,
            2485,
            2680,
            2960,
            3140,
            3405,
            3595,
            3775,
            4050
        ]
    },
    {
        "site": "S3",
        "file": "065819_20170701_0953",
        "type": "bedframe",
        "freq": 6,  # Hz
        "burst_samples": 2048,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.005,  # m
        "T": [  # OBS calibration
            0.422410145065686,
            43.3032571368376,
            287.150660188742,
            544.298765776665,
            680.000456059015,
            812.063983091264,
            929.406146064801,
            1018.65041307351,
            1126.92611241997,
            1228.31827767776,
            1286.42772718125,
            1337.52227002865,
            1396.75846109651,
            1429.94847065443,
            1470.45043664350,
            1480.00354592104,
            1499.18000879259
        ],
        "SSC": [
            0,
            71.7,
            482.5,
            902,
            1175,
            1385,
            1690,
            1950,
            2170,
            2485,
            2680,
            2960,
            3140,
            3405,
            3595,
            3775,
            4050
        ]
    },
    {
        "site": "S4",
        "file": "065821_20170703_1419",
        "type": "bedframe",
        "freq": 6,  # Hz
        "burst_samples": 2048,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.0,  # m
        "T": [  # OBS calibration
            0.498243297801016,
            46.4604577599445,
            318.484915315444,
            592.453008109143,
            741.787167931421,
            891.090314726247,
            1027.35778725457,
            1128.22408110125,
            1225.23696470106,
            1302.51126161141,
            1417.80678845652,
            1465.93272690103,
            1558.34656433677,
            1562.82849734694,
            1605.17982431330,
            1628.62084592690,
            1645.81704983200
        ],
        "SSC": [
            0,
            71.7,
            482.5,
            902,
            1175,
            1385,
            1690,
            1950,
            2170,
            2485,
            2680,
            2960,
            3140,
            3405,
            3595,
            3775,
            4050
        ]
    },
    {
        "site": "S5",
        "file": "065820_20170704_0838",
        "type": "bedframe",
        "freq": 6,  # Hz
        "burst_samples": 2048,  # per burst
        "interval": 600,  # between start of each burst
        "min_depth": 0.0,  # m
        "T": [  # OBS calibration
            0.570033800678927,
            48.9716198321136,
            332.381297507721,
            628.097978952960,
            785.597697034106,
            942.157297509286,
            1091.03889971580,
            1206.08704958744,
            1312.68690924248,
            1401.13378141432,
            1510.00731191590,
            1551.82566339642,
            1630.23432115364,
            1671.74384698519,
            1711.15747166070,
            1760.91130820823,
            1755.81328993499
        ],
        "SSC": [
            0,
            71.7,
            482.5,
            902,
            1175,
            1385,
            1690,
            1950,
            2170,
            2485,
            2680,
            2960,
            3140,
            3405,
            3595,
            3775,
            4050
        ]
    }
]
