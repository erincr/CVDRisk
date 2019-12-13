import pandas as pd
import numpy as np
import scipy
import math

from kmedioids import cluster

import time

def ComputeZipCodeDistances(kms, distances = None, save_path = None):
    if distances is not None:
        # We have already computed the distances - don't recompute!
        distances = np.load(distances)
        return(distances)
    
    def cartesian_product(*arrays):
        la = len(arrays)
        dtype = np.result_type(*arrays)
        arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
        for i, a in enumerate(np.ix_(*arrays)):
            arr[...,i] = a
        return arr.reshape(-1, la)

    all_combos = cartesian_product(
                      kms.index.drop_duplicates().values,
                      kms.DaysToEventOrCensoring.drop_duplicates().sort_values().values
                 )

    all_combos = pd.DataFrame(all_combos).rename({0:"Zipcode_5", 1:"DaysToEventOrCensoring"}, axis=1)
    all_combos.set_index(["Zipcode_5", "DaysToEventOrCensoring"], inplace=True)
    print("Cartesian product done")

    all_combos_merged = all_combos.join(
        kms.reset_index(drop=False).set_index(["Zipcode_5", "DaysToEventOrCensoring"]), 
        how='outer'
    )
    print("Join complete")

    all_combos_merged["n_events"].fillna(0, inplace=True)
    all_combos_merged["n_risk_filled"] = all_combos_merged.groupby("Zipcode_5").n_risk.fillna(method = 'ffill')
    all_combos_merged["n_risk_filled"] = all_combos_merged.groupby("Zipcode_5").n_risk_filled.transform(lambda x: x.fillna(x.max()))

    wide = all_combos_merged[["n_risk_filled", "n_events"]].reset_index().pivot(index = "DaysToEventOrCensoring", columns="Zipcode_5")
    print("Wide data frame ready")
    
    '''
    Compute pairwise distances for all zip code KM curves.
    '''
    def get_one_zip_row(i):
        o1 = wide.loc[:, ('n_events', all_zips[i])].values.reshape(-1, 1)
        n1 = wide.loc[:, ('n_risk_filled', all_zips[i])].values.reshape(-1, 1)

        oall = wide.loc[:, 'n_events'].values
        nall = wide.loc[:, 'n_risk_filled'].values

        ovn = (o1 + oall)/(n1 + nall)

        e1 = ovn.T.dot(n1)
        e2 = (ovn * nall).sum(axis=0).reshape(-1,1)

        return(
            ((o1.sum() - e1)**2/e1 + (oall.sum(axis=0).reshape(-1, 1) - e2)**2/e2).reshape(-1, )
        )

    all_zips = kms.index.drop_duplicates().values
    distances = np.zeros((len(all_zips), len(all_zips)))

    for i in range(len(all_zips)):
        distances[:, i] = distances[i, :] = get_one_zip_row(i)

        if i % 20 == 0:
            print(i)
            print(time.time() - t0)
            t0 = time.time()
            if i % 500 == 0:
                print("SAVED at i = ")
                np.save(save_path, distances)
    np.save(save_path, distances)

def ClusterZipCodes(train, clusterix, distances_path = None, save_path = None):

    kms = train[["Zipcode_5", "DaysToEventOrCensoring", "AnyOutcome"]].copy()
    n_events = kms.groupby(["Zipcode_5", "DaysToEventOrCensoring"]
                          ).AnyOutcome.sum().reset_index().rename({"AnyOutcome":"n_events"}, axis=1)
    
    kms["n_risk"] = kms.groupby("Zipcode_5").DaysToEventOrCensoring.rank(ascending=False, method="first")
    kms = kms.drop("AnyOutcome", axis=1).sort_values(by = "n_risk").groupby(["Zipcode_5", "DaysToEventOrCensoring"]
                                                                           ).last().reset_index()
    kms = kms.merge(n_events)
    
    kms["ri"] = 1 - kms.n_events/kms.n_risk
    kms["vst"] = kms.n_events/((kms.n_risk - kms.n_events)*kms.n_risk)

    kms["St"] = kms.sort_values(by = "DaysToEventOrCensoring", ascending = True).groupby("Zipcode_5").ri.cumprod()
    kms["StVar"] = kms.sort_values(by = "DaysToEventOrCensoring", ascending = True).groupby("Zipcode_5").vst.cumsum()
    kms["StVar"] = kms.St**2 * kms.StVar
    
    kms.set_index("Zipcode_5", inplace=True)
    all_zips = kms.index.drop_duplicates().values
    
    distances = ComputeZipCodeDistances(kms, distances = distances_path, save_path = save_path)
    
    clusts, meds = cluster(distances, clusterix)
    
    return({
        "Clusters" : clusts,
        "Medians"  : meds,
        "KMs"      : kms,
        "AllZips"  : all_zips
    })

    