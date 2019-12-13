import time

import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import metrics


def unoC(t, p, o, w):
    tt = t[t == 1]
    pt = p[t == 1]
    ot = o[t == 1]
    wt = w[t == 1]
    
    def chunked_cindex(chunk, bufsize = len(ot)):
        for start in range(0, bufsize + chunk, chunk):
            s, e = start, min(start + chunk, bufsize)
            print(s)
            oc_bool_matrix = o > ot[s:e].reshape(-1,1)
            pr_bool_matrix = p < pt[s:e].reshape(-1,1)
            both = np.logical_and(oc_bool_matrix, pr_bool_matrix)
        
            n = np.sum(both, axis=1).dot(1/wt[s:e]**2)
            d = np.sum(pr_bool_matrix, axis=1).dot(1/wt[s:e]**2)
            yield n, d
    
    info = [(n,d) for n,d in chunked_cindex(10000)]
    c    = sum([x[0] for x in info])/sum([x[1] for x in info])
    print(c)
    return(c)

def get_metrics(dataset, model, columns):
    df = get_dataset(dataset)
    
    if dataset == "train":
        pr = model.predict_proba(df[df.Censored == 0][columns])[:, 1]
        unoc = 0
    else:
        pr = model.predict_proba(df[columns])[:, 1]
        unoc = unoC(df.AnyOutcome.values, pr, df.DaysToEventOrCensoring.values, df.IPCW.values)
        pr = pr[df.Censored == 0]
    
    
    df = df[df.Censored == 0]
    
    acc    = np.mean(1 * (pr > .5) == df.AnyOutcome.values)
    aucpr  = metrics.average_precision_score(df.AnyOutcome.values, pr)
    aucroc = metrics.roc_auc_score(df.AnyOutcome.values, pr)
    
    return({"unoC_" + dataset: unoc,
            "acc_" + dataset: acc,
            "aucPR_" + dataset: aucpr,
            "aucROC_" + dataset: aucroc
           })

def gb_paramsearch(DEPTH, COLUMNS, COLNAME, START = 0, ENDIX = 11):
    gbt = pd.DataFrame({
              "trees": range(START, 1600), 
              "columns": COLNAME, 
              "depth" : DEPTH,
              "unoC_train": 0,
              "acc_train": 0,
              "aucPR_train": 0,
              "aucROC_train": 0,
              "unoC_val": 0,
              "acc_val": 0,
              "aucPR_val": 0,
              "aucROC_val": 0})

    gb = GradientBoostingClassifier(
            random_state=0, 
            verbose = True,
            min_samples_leaf = 5,
            max_depth = DEPTH,
            n_estimators = START,
            subsample = 1,
            learning_rate=0.1
    )
    if START > 0:
        print("pretraining!")
        gb.fit(
           train.loc[tra_ix, COLUMNS], 
           train.loc[tra_ix, "AnyOutcome"], 
           sample_weight = train.loc[tra_ix, "IPCW"]
        )
    
    
    t0 = time.time()
    for i in range(1, ENDIX):
        if i % 10 == 0:
            print(i)
            print(time.time() - t0)
            t0 = time.time()
            
        _ = gb.set_params(n_estimators= START + 20 * i, warm_start=True) 

        gb.fit(
           train.loc[tra_ix, COLUMNS], 
           train.loc[tra_ix, "AnyOutcome"], 
           sample_weight = train.loc[tra_ix, "IPCW"]
        )
        print(gb.n_estimators_)

        for d in ["train", "val"]:
            gc.collect()
            ms = get_metrics(d, gb, COLUMNS) #get_metrics(d, gb, COLUMNS)
            print(ms)
            for k, v in ms.items():
                gbt.loc[gbt.trees == gb.n_estimators_, k] = v
                
    gbt = gbt[~(gbt.unoC_val == 0)].reset_index(drop=True)
    previous = pd.read_csv("./Performance_Metrics/metric_df.csv")
    
    gbt = pd.concat([previous, gbt])
    print("Finished! We have this many rows in our data frame:", len(gbt))
    gbt.to_csv("./Performance_Metrics/metric_df.csv", index=False)