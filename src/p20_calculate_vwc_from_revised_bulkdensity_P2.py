import glob
import pathlib
import pandas as pd
import datetime

from common import *

def main(
    pathRevisedBulkDensity: pathlib.Path,
    pathGwcDir: pathlib.Path,
    workingDir: pathlib.Path,
    outputDir: pathlib.Path,
    useCache: bool
):    
    ### Data Preparation
    pathGravimetricWCIntermediate = workingDir / "21_gravimetricWCAggregate.csv"
    pathGravimetricWCTidy = workingDir / "22_gravimetricWCTidy.csv"
    pathBulkDensityIntermediate = workingDir / "23_bulkDensityPerFootIntermediate.csv"
    pathBulkDensityTidy = workingDir / "24_bulkDensityPerFootTidy.csv"

    # Create working dir if not exist
    workingDir.mkdir(parents=True, exist_ok=True)

    # Aggregate files with gravimetric water content
    if((not useCache) | (not pathGravimetricWCIntermediate.is_file())):
        gwcAggregate = getGwcNMeasured(
            pathGwcDir,
            [0, 1, 2, 3],
            ["ID2", "GravimetricWaterContent", "Ammonia", "Nitrate"])
        gwcAggregate.to_csv(pathGravimetricWCIntermediate, index=False)
    else:
        gwcAggregate = pd.read_csv(pathGravimetricWCIntermediate)

    # Convert aggregated vwc data to tidy format
    if((not useCache) | (not pathGravimetricWCTidy.is_file())):
        gwcTidy = tidyGwcNMeasuredAggregate(
            gwcAggregate)
        gwcTidy.to_csv(pathGravimetricWCTidy, index=False)
    else:
        gwcTidy = pd.read_csv(pathGravimetricWCTidy)

    # Read revised bulk density data and calculate values for 1 ft intervals
    if((not useCache) | (not pathBulkDensityIntermediate.is_file())):
        bulkDensity = getRevisedBulkDensity(pathRevisedBulkDensity)
        bdPerFootIntermediate = transformBDPerHorizonToFoot(bulkDensity)
        bdPerFootIntermediate.to_csv(pathBulkDensityIntermediate)
    else:
        bdPerFootIntermediate = pd.read_csv(pathBulkDensityIntermediate)

    if((not useCache) | (not pathBulkDensityTidy.is_file())):
        bdPerFoot = cleanBDPerFootIntermediate(bdPerFootIntermediate)
        bdPerFoot.to_csv(pathBulkDensityTidy, index=False)
    else:
        bdPerFoot = pd.read_csv(pathBulkDensityTidy)
    
    df = calculateVwcFromGwc(gwcTidy, bdPerFoot)
    df = df.rename(columns={
        "Year_x": "Year",
        "TopDepth_x": "TopDepth"})
    df = df[[
        "Year", 
        "Season", 
        "ID2", 
        "Latitude", 
        "Longitude", 
        "TopDepth", 
        "BottomDepth", 
        "BulkDensity", 
        "GravimetricWaterContent", 
        "VolumetricWaterContent",
        "Nitrate",
        "Ammonia",
        "Notes"]]
    df = df.sort_values(by=["Year", "Season", "ID2"])
    df = df.dropna(axis=0, subset=["VolumetricWaterContent"])

    # Write final dataset
    outputDir.mkdir(parents=True, exist_ok=True)
    date_today = datetime.datetime.now().strftime("%Y%m%d")
    df.to_csv(
        outputDir / "VolumetricWaterContentFromRevisedBd_P2_{}.csv".format(date_today), 
        index = False)
    
if __name__ == "__main__":
    # parameters
    inputDir = pathlib.Path.cwd() / "data" / "input"
    workingDir = pathlib.Path.cwd() / "data" / "working"
    outputDir = pathlib.Path.cwd() / "data" / "output"
    inputRevisedBulkDensity = inputDir / "soilCore1998To2015ShallowDeepMergedByHorizon_20201221.csv"
    inputGwcNMeasuredDir = inputDir / "GwcInorganicNMeasured"

    main(
        inputRevisedBulkDensity,
        inputGwcNMeasuredDir,
        workingDir,
        outputDir,
        False
    )