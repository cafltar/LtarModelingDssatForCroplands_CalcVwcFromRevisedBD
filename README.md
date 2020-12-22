# README

## Purpose

Calculate volumetric water content using legacy gravimetric water content measurements and revised/QC'd/Production-level bulk density values.

The gravimetric data was originally used to calculate volumetric through "representitive" bulk density values taken at locations with similar soil types instead of the same location that gravimetric was measured. This effort is to use more representitive bulk density data.

See: [https://doi.org/10.1016/j.jhydrol.2011.04.029]

## Files

Script and output files have a prefix (e.g. "p00_") to represent their sequential step in data processing. The letter "p" represents "processing" followed by a major number and a minor number.

* [src/common.py](src/common.py)
  * Contains common functions used by processing scripts and notebooks
* [src/p00_calculate_vwc_from_revised_bulkdensity.py](src/p00_calculate_vwc_from_revised_bulkdensity.py)
  * The script aggregates modeled and measured gravimetric water content data from Hesham's work, aggregates and cleans bulk density data from 1998, and calculates volumetric water content
* [notebooks/p10_review_vwc.ipynb](notebooks/p10_review_vwc.ipynb)
  * Visualizations for assessing [src/p00_calculate_vwc_from_revised_bulkdensity.py](src/p00_calculate_vwc_from_revised_bulkdensity.py)
* [src/p20_calculate_vwc_from_revised_bulkdensity_P02.py](src/p20_calculate_vwc_from_revised_bulkdensity_P02.py)
  * This is the third script to be run; it references many functions defined in [src/p00_calculate_vwc_from_revised_bulkdensity.py](src/p00_calculate_vwc_from_revised_bulkdensity.py)
  * The difference between this script and [src/p00_calculate_vwc_from_revised_bulkdensity.py](src/p00_calculate_vwc_from_revised_bulkdensity.py) is that this script only handles measured GWC data, not both measured and modeled
* [notebooks/p30_review_vwc_from_measured.ipynb](notebooks/p30_review_vwc_from_measured.ipynb)
  * Visualizations for assessing [src/p20_calculate_vwc_from_revised_bulkdensity_P02.py](src/p20_calculate_vwc_from_revised_bulkdensity_P02.py)

## Processing steps

Both scripts in the src folder have the same general processing steps:

1. Set parameters (input paths, whether to load cached datasets or not)
2. Aggregate raw datasets with GWC
3. Clean and tidy GWC data
4. Read in bulk density data
5. Calculate bulk density data for 1 foot increments from native increments (0-10 cm, 10-20 cm, 20-30 cm, then by horizon). Calculation is based on weighted average:

    ```python
        row["TopDepthWeighted"] = topDepth if (row["TopDepthFt"] < topDepth) else row["TopDepthFt"]
        row["BottomDepthWeighted"] = (topDepth + increment) if (row["BottomDepthFt"] > (topDepth + increment)) else row["BottomDepthFt"]

        row["Weight"] = (row["BottomDepthWeighted"] - row["TopDepthWeighted"]) / increment
        row["BulkDensityWeighted"] = row["Weight"] * row["BulkDensity"]
    ```

6. Combine GWC and BD data
7. Calculate VWC from GWC and BD data (VWC = GWC * BD)
8. Write output

## License

As a work of the United States government, this project is in the public domain within the United States.

Additionally, we waive copyright and related rights in the work worldwide through the CC0 1.0 Universal public domain dedication.
