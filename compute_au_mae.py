#!/usr/bin/env python3
# compute_au_mae.py

import pandas as pd, numpy as np

def main():
    w = {'AU1':1,'AU2':1,'AU4':1,'AU6':2,'AU12':2}
    df_r = pd.read_csv("aus/real.csv")
    df_g = pd.read_csv("aus/gen.csv")
    maes = []
    for au,wt in w.items():
        maes.append(wt * np.abs(df_r[au] - df_g[au]))
    score = (sum(maes)/sum(w.values())).mean()
    print("AU MAE:", score)

if __name__=='__main__':
    main()
