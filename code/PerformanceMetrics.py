import numpy as np


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
