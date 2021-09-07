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
  * Notes from [CAF_outline.docx] suggest that these values are the "final" ones used for analysis and include measured and modeled values (through a "simple correlation")

## 11/17/2020

* [InorganicNitrogen](InorganicNitrogen)
  * From Bryan Carlson's Google Drive: [My Drive/Archive/NasRm243_20160615_oldDataBackup/DataDriveBackup/Projects/Individual_Users/Hesham/Cook_Farm/Excel/original]
  * Has ammonia and nitrate values in a consistent format from 1999-2006
  * Looks like ID2 values are missing (sl_unique_id doesn't seem to match ID2)
  * Data should be compared to data in [VwcSpringFallCalc] using GWC values
  
## 11/18/2020
 
 * [CAF_outline.docx](CAF_outline.docx)
   * From Bryan Carlson's Google Drive: [My Drive/Archive/NasRm243_20160615_oldDataBackup/DataDriveBackup/Projects/Individual_Users/Hesham/Cook_Farm]
   * Has detailed notes on methods and file descriptions for Hesham's files. This is gold, baby!
 * [GwcInorganicNMeasured](GwcInorganicNMeasured)
   * From Bryan Carlson's Google Drive: [My Drive/Archive/NasRm243_20160615_oldDataBackup/DataDriveBackup/Projects/Individual_Users/Hesham/Cook_Farm/SAS_inf]
   * Files with, what seem to be, measured values of GWC, ammonia, and nitrate with ID2 values
   * File name in form: Soil3{F/S for spring/fall}{Depth in foot}_{two digit year}.xls

## 12/21/2020

* [soilCore1998To2015ShallowDeepMergedByHorizon_20201221.csv](soilCore1998To2015ShallowDeepMergedByHorizon_20201221.csv)
  * From: CookEastSoilGridPointSurvey\R\MergeDepthsAndYears\output
  * Updated from previous version after fixing copy/paste error with a bulk density value (ID2=189, HY1998 and 2008) and removing 0 values that should be NA (pH, C, N related values)

## 09/07/2021

* [CookEastSoilGwcDates_20210903.xlsx](CookEastSoilGwcDates_20210903.xlsx)
  * From: LtarModelingDssatForCroplands\Working\DetermineSamplingDatesForGwc
  * Has concrete dates for soil sampling for original GWC analysis. These dates will add context to the data in addition to the current "season" designation (Spring/Fall)
