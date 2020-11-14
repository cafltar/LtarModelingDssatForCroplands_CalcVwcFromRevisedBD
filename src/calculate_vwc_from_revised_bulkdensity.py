import glob
import pathlib
import pandas as pd
import datetime

def convertTwoDigitYearToFourDigit(shortYear):
    if(shortYear > 10):
        longYear = shortYear + 1900
    else:
        longYear = shortYear + 2000
    
    return longYear

def readGwcFile(filePath, seasonDesignation, colkeep, colnames):
    # returns a dataframe of GWC data with year and season appended
    df = pd.read_excel(
        filePath,
        usecols=colkeep,
        names=colnames
    )

    df["Year"] = int(filePath.stem[-2:])
    df["Season"] = seasonDesignation

    return df

def getGravimetricWaterContent(
    gwcDir: pathlib.Path
):
    colkeep = [0, 8, 9, 10, 11, 12]
    colnames = ["ID2", "GWC_1", "GWC_2", "GWC_3", "GWC_4", "GWC_5"]

    df = pd.DataFrame()

    seasons = ["Spring", "Fall"]

    for season in seasons:
        for name in gwcDir.glob("VWC" + season[0:1] + "*.xls"):
            print(name)
            df_year = readGwcFile(name, season, colkeep, colnames)
            df = df.append(df_year)

    df["Year"] = df["Year"].apply(lambda x: convertTwoDigitYearToFourDigit(x))

    return df

def getRevisedBulkDensity(
    bdPath: pathlib.Path
):
    df = pd.read_csv(
        bdPath,
        usecols=[0,1,2,3,4,5,7]
    )
    df_1998 = df[df["Year"] == 1998]
    
    return df_1998

def transformBDPerHorizonToFoot(
    bdPerHorizon: pd.DataFrame
):
    CM_TO_FT = 0.0328084
    INCREMENT = 1
    TOP_DEPTHS = list(range(0,5,INCREMENT))
    
    # Copy bd df, convert depth increments from cm to ft
    # Get dataframe with just year and ID2
    # For each row in year+id2 df
    #   For each depth increment (int i = 0, i+1, i<=4)
    #       get rows from bd_df where id2 match, year match, topdepth or bottomdepth >= i (depth increment)
    #       for each row
    #           topDepth = row.topDepth < i ? i : topDepth
    #           bottomDepth = row.bottomDepth > i+1 ? i+1 : bottomDepth
    #           weight = (bottomDepth - topDepth) / 1
    #           weightedBD = weight * row.BulkDensity
    #       check sum of weight == 1
    #       bd_df.TopDepthFt = i
    #       bd_df.BottomDepthFt = i + 1

    bdPerHorizonFt = bdPerHorizon.copy()
    bdPerHorizonFt = bdPerHorizonFt.assign(TopDepthFt = lambda x: x["TopDepth"] * CM_TO_FT)
    bdPerHorizonFt = bdPerHorizonFt.assign(BottomDepthFt = lambda x: x["BottomDepth"] * CM_TO_FT)

    # Get samples for loop
    samples = bdPerHorizon[["Year", "ID2"]].drop_duplicates()
    bdPerFt = pd.DataFrame()

    for index, row in samples.iterrows():
        sample_df = bdPerHorizonFt.loc[(bdPerHorizonFt["Year"] == row["Year"]) & (bdPerHorizonFt["ID2"] == row["ID2"])]
        for topDepth in TOP_DEPTHS:
            print(row["Year"], row["ID2"], topDepth)
            
            sample_depth_df = sample_df.loc[
                (((sample_df["TopDepthFt"] >= topDepth) | 
                    (sample_df["BottomDepthFt"] >= topDepth)) & 
                ((sample_df["TopDepthFt"] <= (topDepth + INCREMENT)) | 
                    (sample_df["BottomDepthFt"] <= (topDepth + INCREMENT))))]
            
            if(len(sample_depth_df) > 0):
                sample_depth_df = sample_depth_df.apply(
                    lambda x : calculateWeightedBulkDensity(x, topDepth, INCREMENT), 
                    axis = 1)

                sum_of_weights = sample_depth_df["Weight"].sum()
                if(sum_of_weights) != 1:
                    msg = "WARNING: Sum of weights does not equal 1"
                    sample_depth_df["Notes"] = msg if not set(["Notes"]).issubset(sample_depth_df) else (sample_depth_df["Notes"] + " | " + msg)
                    #raise Exception("Sum of weights does not equal 1")

                bulk_density_per_increment = sample_depth_df["BulkDensityWeighted"].sum()
                if(bulk_density_per_increment):
                    sample_depth_df["BulkDensityPerIncrement"] = bulk_density_per_increment
                sample_depth_df["DepthIncrementTop"] = topDepth
                sample_depth_df["DepthIncrementBottom"] = topDepth + INCREMENT
                
                bdPerFt = bdPerFt.append(sample_depth_df)

    return bdPerFt

def calculateWeightedBulkDensity(row, topDepth, increment):
    row["TopDepthWeighted"] = topDepth if (row["TopDepthFt"] < topDepth) else row["TopDepthFt"]
    row["BottomDepthWeighted"] = (topDepth + increment) if (row["BottomDepthFt"] > (topDepth + increment)) else row["BottomDepthFt"]

    row["Weight"] = (row["BottomDepthWeighted"] - row["TopDepthWeighted"]) / increment
    row["BulkDensityWeighted"] = row["Weight"] * row["BulkDensity"]
    
    return row

def cleanBDPerFootIntermediate(bdPerFoot):
    df = bdPerFoot[["Year", "ID2", "Latitude", "Longitude", "DepthIncrementTop", "DepthIncrementBottom", "BulkDensityPerIncrement", "Notes"]]
    df = df.rename(columns={"DepthIncrementTop": "TopDepth", "DepthIncrementBottom": "BottomDepth", "BulkDensityPerIncrement": "BulkDensity"})
    df = df.drop_duplicates()

    return df

def tidyGwcAggregate(gwcAggregate):
    df = gwcAggregate.copy()

    df = pd.melt(df,
        ["ID2", "Year", "Season"],
        var_name = "DepthLabel",
        value_name = "GravimetricWaterContent")

    df["BottomDepth"] = df.apply(lambda x: int(x["DepthLabel"].split("_")[1]), axis = 1)

    df = df[["ID2", "Year", "Season", "BottomDepth", "GravimetricWaterContent"]]

    return df

def calculateVwcFromGwc(gwcTidy, bdPerFoot):
    gwc = gwcTidy.copy()
    bd = bdPerFoot.copy()

    df = gwc.merge(bd, on = ["ID2", "BottomDepth"], how = "left")
    df["VolumetricWaterContent"] = df.apply(lambda x: x["GravimetricWaterContent"] * x["BulkDensity"], axis = 1)

    return df

def main(
    pathRevisedBulkDensity: pathlib.Path,
    pathGwcDir: pathlib.Path,
    workingDir: pathlib.Path,
    useCache: bool
):    
    ### Data Preparation
    pathGravimetricWCIntermediate = workingDir / "01_gravimetricWCAggregate.csv"
    pathGravimetricWCTidy = workingDir / "02_gravimetricWCTidy.csv"
    pathBulkDensityIntermediate = workingDir / "03_bulkDensityPerFootIntermediate.csv"
    pathBulkDensityTidy = workingDir / "04_bulkDensityPerFootTidy.csv"

    # Create working dir if not exist
    workingDir.mkdir(parents=True, exist_ok=True)

    # Aggregate files with gravimetric water content
    if((not useCache) | (not pathGravimetricWCIntermediate.is_file())):
        gwcAggregate = getGravimetricWaterContent(pathGwcDir)
        gwcAggregate.to_csv(pathGravimetricWCIntermediate, index=False)
    else:
        gwcAggregate = pd.read_csv(pathGravimetricWCIntermediate)

    # Convert aggregated vwc data to tidy format
    if((not useCache) | (not pathGravimetricWCTidy.is_file())):
        gwcTidy = tidyGwcAggregate(gwcAggregate)
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
    df = df.rename(columns={"Year_x": "Year"})
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
        "Notes"]]
    df = df.sort_values(by=["Year", "Season", "ID2"])
    df = df.dropna(axis=0, subset=["VolumetricWaterContent"])

    # Write final dataset
    date_today = datetime.datetime.now().strftime("%Y%m%d")
    df.to_csv(
        workingDir / "VolumetricWaterContentFromRevisedBd_{}.csv".format(date_today), 
        index = False)
    
if __name__ == "__main__":
    # parameters
    inputDir = pathlib.Path.cwd() / "input"
    inputRevisedBulkDensity = inputDir / "soilCore1998To2015ShallowDeepMergedByHorizon_20180926.csv"
    inputGwcDir = inputDir / "VwcSpringFallCalc"
    workingDir = pathlib.Path.cwd() / "working"
    
    main(
        inputRevisedBulkDensity,
        inputGwcDir,
        workingDir,
        True
    )