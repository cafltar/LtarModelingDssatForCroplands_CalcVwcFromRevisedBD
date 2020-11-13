import glob
import pathlib
import pandas as pd

def readGwcFile(filePath, seasonDesignation, colkeep, colnames):
    # returns a dataframe of GWC data with year and season appended
    df = pd.read_excel(
        filePath,
        usecols=colkeep,
        names=colnames
    )

    df["Year"] = filePath.stem[-2:]
    df["Season"] = seasonDesignation

    return df

def getGravimetricWaterContent(
    gwcDir: pathlib.Path
):
    colkeep = [0, 8, 9, 10, 11, 12]
    colnames = ["ID2", "GWC_1", "GWC_2", "GWC_3", "GWC_4", "GWC_5"]

    df = pd.DataFrame()

    seasons = ["S", "F"]

    for season in seasons:
        for name in gwcDir.glob("VWC" + season + "*.xls"):
            print(name)
            df_year = readGwcFile(name, season, colkeep, colnames)
            df = df.append(df_year)

    df.to_csv("foo.csv")

def main(
    pathRevisedBulkDensity: pathlib.Path,
    pathGwcDir: pathlib.Path
):
    ### Data Preparation
    getGravimetricWaterContent(pathGwcDir)

if __name__ == "__main__":
    # parameters
    inputDir = pathlib.Path.cwd() / "input"
    inputRevisedBulkDensity = inputDir / "soilCore1998To2015ShallowDeepMergedByHorizon_20180926.csv"
    inputGwcDir = inputDir / "VwcSpringFallCalc"
    
    main(
        inputRevisedBulkDensity,
        inputGwcDir
    )