## Requirements

To run `preprocess.m` you need the RSKTools and gsw packages:

- [RSKTools for MATLAB](https://rbr-global.com/support/matlab-tools)
- [Gibbs-SeaWater (GSW) Oceanogrpahic Toolbox](http://www.teos-10.org/software.htm#1)

## Preprocess

Derive pressure, depth and salinity variables. Time period between 12PM 11th May (UTC) and 12PM 9th June (UTC), first quarter to first quarter of the Lunar calendar.

A2D zero-hold correction for original data variables, filling the gaps with interpolated values. See the [offical docs](https://docs.rbr-global.com/rsktools/process/post-processors/rskcorrecthold-m).

Generated files saved as new 'RSK' files.