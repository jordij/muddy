# MUDDY - Sediment Dynamics

## Requirements

- Install Anaconda https://www.anaconda.com/distribution/#download-section
- Install requirements.txt:

```$ conda create -n new environment --file req.txt```

## Steps

Create folder structure:

`$ python structure.py`

Generate transect, elevation profile and sites maps (pngs in `/output/`):

`$ python sitesmap.py`
`$ python bathymetry.py`
`$ python transect.py`

Generate daily separate plots for all sites/concertos/variables:

`$ python concerto.py --plot_all=False`

`plot_all` to `True` generates a single figure per day containing all available variables. Setting it to `False` generates a separate figure for pair of variable/day.

Check all the generated assets in the `./output` folder.


*Warning* you better have some memory available before running this puppy :D