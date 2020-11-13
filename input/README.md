# Files
  
## 11/04/2020

* [WaterData_dirty](WaterData_dirty)
  * Copied from [Working\DataOrganization\Soil]
  * Originally from David Huggins via emails "1999 water data", "2001 water data", "2000 water data" on 07/16/2020
  * Data with gavimetric water content that need to be combined with cleaned bulk density data to get volumentric water content. Data are from spring prior to planting and fall after harvest. Data are in different depth increments that need to be consolidated.

## 11/10/2020

* [soilCore1998To2015ShallowDeepMergedByHorizon_20180926.csv](soilCore1998To2015ShallowDeepMergedByHorizon_20180926.csv)
  * From cafltardatalake/production/CookEastSoilGridPointSurvey/SoilCore1999To2015ShallowDeepMergedByHorizon_v1/
  * [https://cafltardatalake.blob.core.windows.net/production/CookEastSoilGridPointSurvey/SoilCore1999To2015ShallowDeepMergedByHorizon_v1/soilCore1998To2015ShallowDeepMergedByHorizon_20180926.csv]
  * Has revised bulk density values that should be used with gravimetric data found in [WaterData_dirty]

## 11/12/2020
* [All_VWC_Cor_F1_99_06.xls](All_VWC_Cor_F1_99_06.xls)
  * From Bryan Carlson's Google Drive: [My Drive/Archive/NasRm243_20160615_oldDataBackup/DataDriveBackup/Projects/Individual_Users/Hesham/Cook_Farm/Excel/VWC/VWC_feet]
  * Has aggregated volumetric water content calculated using, I'm assuming, representative bulk density for the soil type. These can be used to validate ball-park values compared to values calculated using revised bulk density
* [VwcSpringFallCalc](VwcSpringFallCalc)
  * From Bryan Carlson's Google Drive: [My Drive/Archive/NasRm243_20160615_oldDataBackup/DataDriveBackup/Projects/Individual_Users/Hesham/Cook_Farm/Excel/VWC/VWC_feet]
  * Looks to include raw values and calculations
  * Filename format seems to be: "VWC{F,S}{YY}.xls" where {F,S} is fall or spring, respectively, {YY} is two digit year (99 = 1999, 00 = 2000).
