import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def PrepareData(datapath, zipdatapath):
    dt    = pd.read_csv(datapath)
    dtzip = pd.read_csv(zipdatapath)

    dt["Censor_Date_Datetime"] = pd.to_datetime(dt.Censor_Date)
    dt["Index_Date_Datetime"]  = pd.to_datetime(dt.Index_Date)
    dt["Index_Date_Plus_10_Years"] = pd.to_datetime(dt.Index_Date_Plus_10_Years)
    dt["Outcome_Date_Datetime"] = pd.to_datetime(dt.Outcome_Date)
    dt["DaysToCensoring"] = dt.Censor_Date_Datetime - dt.Index_Date_Datetime

    # This should be ~8%
    print("Prevalence: ", dt.AnyOutcome.sum()/len(dt))

    # ~14,000
    print("Number of ZIP codes:", len(dt.Zipcode_5.drop_duplicates()))

    zips = dt.Zipcode_5.drop_duplicates()
    clean_zips = pd.DataFrame(
        {"unique_zip": [x[0] if len(x) > 0 else "" for x in [[y for y in x.split("_") if y in dtzip.Zip.values] for x in zips]],
         "grouped_zip": zips
        }
    )
    fixedzips = dtzip.merge(clean_zips, left_on = "Zip", right_on = "unique_zip")

    dt = dt.merge(fixedzips, left_on = "Zipcode_5", right_on = "grouped_zip")
    dt.drop("unique_zip", axis=1, inplace=True) 

    dt["DaysToCensoring"] = dt.Censor_Date_Datetime - dt.Index_Date_Datetime
    dt["WeeksToCensoring"] = np.ceil(dt.DaysToCensoring.dt.days/7)

    dt["Censored"] = 1
    dt.loc[(dt.AnyOutcome == 0) & (dt.DaysToCensoring.dt.days >= 10 * 365.25), "Censored"] = 0
    dt.loc[dt.AnyOutcome == 1, "Censored"] = 0

    dt['Gdr_M'] = 0
    dt.loc[dt.Gdr_Cd == 'M', 'Gdr_M'] = 1

    dtOutcome     = dt.loc[dt.AnyOutcome == 1]
    dtNoOutcome   = dt.loc[dt.AnyOutcome == 0]

    train1, test1 = train_test_split(dtOutcome, test_size=0.2, random_state=42)
    val1, test1   = train_test_split(test1, test_size=0.5, random_state=42)

    train0, test0 = train_test_split(dtNoOutcome, test_size=0.2, random_state=42)
    val0, test0   = train_test_split(test0, test_size=0.5, random_state=42)

    train = pd.concat([train1, train0]).reset_index()
    test  = pd.concat([test1, test0]).reset_index()
    val   = pd.concat([val1, val0]).reset_index()

    print(len(train) + len(test) + len(val) == len(dt))
    print(train.AnyOutcome.sum()/len(train))
    print(test.AnyOutcome.sum()/len(test))
    print(val.AnyOutcome.sum()/len(val))
    
    return({
        "Train": train,
        "Test" : test,
        "Val"  : val,
        "Zips" : fixedzips
    })