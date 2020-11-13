import glob
import pathlib
import pandas as pd

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

    return df

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

    bdPerFt = bdPerHorizon.copy()
    bdPerFt = bdPerFt.assign(TopDepthFt = lambda x: x["TopDepth"] * CM_TO_FT)
    bdPerFt = bdPerFt.assign(BottomDepthFt = lambda x: x["BottomDepth"] * CM_TO_FT)

    # Get samples for loop
    samples = bdPerHorizon[["Year", "ID2"]].drop_duplicates()

    for index, row in samples.iterrows():
        sample_df = bdPerFt.loc[(bdPerFt["Year"] == row["Year"]) & (bdPerFt["ID2"] == row["ID2"])]
        for topDepth in TOP_DEPTHS:
            print(row["Year"], row["ID2"], topDepth)
            
            sample_depth_df = sample_df.loc[(((sample_df["TopDepthFt"] >= topDepth) | (sample_df["BottomDepthFt"] >= topDepth)) & ((sample_df["TopDepthFt"] <= (topDepth + INCREMENT)) | (sample_df["BottomDepthFt"] <= (topDepth + INCREMENT))))]
            print("sample_depth_df")
            print(sample_depth_df)
            sample_depth_df = sample_depth_df.apply(lambda x : calculateWeightedBulkDensity(x, topDepth, INCREMENT), axis = 1)
            print(sample_depth_df)

    return bdPerFt

def calculateWeightedBulkDensity(row, topDepth, increment):
    row["TopDepthWeighted"] = topDepth if (row["TopDepthFt"] < topDepth) else row["TopDepthFt"]
    row["BottomDepthWeighted"] = (topDepth + increment) if (row["BottomDepthFt"] > (topDepth + increment)) else row["BottomDepthFt"]

    row["Weight"] = (row["BottomDepthWeighted"] - row["TopDepthWeighted"]) / increment
    row["BulkDensityWeighted"] = row["Weight"] * row["BulkDensity"]
    
    return row

def main(
    pathRevisedBulkDensity: pathlib.Path,
    pathGwcDir: pathlib.Path
):    
    ### Data Preparation
    #getGravimetricWaterContent(pathGwcDir)
    bulkDensity = getRevisedBulkDensity(pathRevisedBulkDensity)
    bdPerFoot = transformBDPerHorizonToFoot(bulkDensity)

    
if __name__ == "__main__":
    # parameters
    inputDir = pathlib.Path.cwd() / "input"
    inputRevisedBulkDensity = inputDir / "soilCore1998To2015ShallowDeepMergedByHorizon_20180926.csv"
    inputGwcDir = inputDir / "VwcSpringFallCalc"
    
    main(
        inputRevisedBulkDensity,
        inputGwcDir
    )