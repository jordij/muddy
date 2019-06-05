# MUDDY - Sediment Dynamics

## Requirements

- Install Anaconda https://www.anaconda.com/distribution/#download-section
- Install requirements.txt:

```$ conda create -n new environment --file req.txt```

## Steps

Create folder structure:

`$ python muddy.py create_struct`

Generate transect, elevation profile and sites maps (pngs in `/output/`):

`$ python muddy.py create_maps`

Generate daily daily plots for all sites/concertos/variables:

`$ python muddy.py daily_plots`

Check all the generated assets under the `./plots` folder.
