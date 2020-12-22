import glob
import pathlib
import pandas as pd

# Converts a one or two digit year (e.g. 0 for 2000) found between 1999-2006 to four digit year
def convertTwoDigitYearToFourDigit(shortYear):
    if(shortYear > 10):
        longYear = shortYear + 1900
    else:
        longYear = shortYear + 2000
    
    return longYear

# Loads bulk bulk density values from 1998 from CookEastSoilGridPointSurvey/soilCore1998To2015ShallowDeepMergedByHorizon dataset
def getRevisedBulkDensity(
    bdPath: pathlib.Path
):
    df = pd.read_csv(
        bdPath,
        usecols=[0,1,2,3,4,5,7]
    )
    df_1998 = df[df["Year"] == 1998]
    
    return df_1998

# Converts bulk density data from 0-10 cm, 10-20 cm, 20-30 cm, by horizon to 1 foot increments (0-1,1-2,2-3,3-4). Uses a weighted average to do this.
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

# Cleans BD at foot intevals data; selects, renames, drops duplicates
def cleanBDPerFootIntermediate(bdPerFoot):
    df = bdPerFoot[["Year", "ID2", "Latitude", "Longitude", "DepthIncrementTop", "DepthIncrementBottom", "BulkDensityPerIncrement", "Notes"]]
    df = df.rename(columns={"DepthIncrementTop": "TopDepth", "DepthIncrementBottom": "BottomDepth", "BulkDensityPerIncrement": "BulkDensity"})
    df = df.drop_duplicates()

    return df

# Loads and aggregates measured GWC data in various xls files
def getGwcNMeasured(
    gwcDir: pathlib.Path,
    colKeep: list,
    colNames: list
):
    col_keep = colKeep
    col_names = colNames

    df = pd.DataFrame()

    seasons = ["Spring", "Fall"]
    bottomDepths = [1,2,3,4,5]

    for season in seasons:
        for bottomDepth in bottomDepths:
            for name in gwcDir.glob("Soil3" + season[0:1] + str(bottomDepth) + "*.xls"):
                df_file = pd.read_excel(
                    name,
                    "Sheet1",
                    usecols=col_keep,
                    names=col_names)
                df_file["Year"] = int(name.stem[-2:])
                df_file["Season"] = season
                df_file["BottomDepth"] = bottomDepth

                df = df.append(df_file)
    
    return df

# Creates TopDepth and cleans Year data from measured GWC data
def tidyGwcNMeasuredAggregate(
    gwcAggregate: pd.DataFrame):

    df = gwcAggregate.copy()

    df["TopDepth"] = df["BottomDepth"] - 1
    df["Year"] = df["Year"].apply(lambda x: convertTwoDigitYearToFourDigit(x))

    df = df[["ID2", "Year", "Season", "TopDepth", "BottomDepth", "GravimetricWaterContent", "Nitrate", "Ammonia"]]

    return df

# Helper method for getVwcSpringFallCalcAggregate()
def readVwcSpringFallCalcFile(filePath, seasonDesignation, colkeep, colnames):
    # returns a dataframe of GWC data with year and season appended
    df = pd.read_excel(
        filePath,
        usecols=colkeep,
        names=colnames
    )

    df["Year"] = int(filePath.stem[-2:])
    df["Season"] = seasonDesignation

    return df

# Reads GWC from various excel files, data also includes VWC data from "legacy" methods
def getVwcSpringFallCalcAggregate(
    gwcDir: pathlib.Path,
    colKeep: list,
    colNames: list
):
    col_keep = colKeep
    col_names = colNames

    df = pd.DataFrame()

    seasons = ["Spring", "Fall"]

    for season in seasons:
        for name in gwcDir.glob("VWC" + season[0:1] + "*.xls"):
            #print(name)
            df_year = readVwcSpringFallCalcFile(name, season, col_keep, col_names)
            df = df.append(df_year)

    df["Year"] = df["Year"].apply(lambda x: convertTwoDigitYearToFourDigit(x))

    return df

# Calculates weighted bulk density data, used by transformBDPerHorizonToFoot()
def calculateWeightedBulkDensity(row, topDepth, increment):
    row["TopDepthWeighted"] = topDepth if (row["TopDepthFt"] < topDepth) else row["TopDepthFt"]
    row["BottomDepthWeighted"] = (topDepth + increment) if (row["BottomDepthFt"] > (topDepth + increment)) else row["BottomDepthFt"]

    row["Weight"] = (row["BottomDepthWeighted"] - row["TopDepthWeighted"]) / increment
    row["BulkDensityWeighted"] = row["Weight"] * row["BulkDensity"]
    
    return row

# Cleans dataset from aggregated GWC (and VWC) with modeled values; melts, adds BottomDepth, drops/rearranges cols
def tidyVwcSpringFallCalcAggregate(
    gwcAggregate: pd.DataFrame,
    valueName: str):
    df = gwcAggregate.copy()

    df = pd.melt(df,
        ["ID2", "Year", "Season"],
        var_name = "DepthLabel",
        value_name = valueName)

    df["BottomDepth"] = df.apply(lambda x: int(x["DepthLabel"].split("_")[1]), axis = 1)

    df = df[["ID2", "Year", "Season", "BottomDepth", valueName]]

    return df

# Calculates VWC from GWC and BD
def calculateVwcFromGwc(gwcTidy, bdPerFoot):
    gwc = gwcTidy.copy()
    bd = bdPerFoot.copy()

    df = gwc.merge(bd, on = ["ID2", "BottomDepth"], how = "left")
    df["VolumetricWaterContent"] = df.apply(lambda x: x["GravimetricWaterContent"] * x["BulkDensity"], axis = 1)

    return df
