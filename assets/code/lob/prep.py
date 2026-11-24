# Convert Binance bookTicker / aggTrades CSVs to compact numpy files
import pandas as pd, numpy as np, sys, glob
for f in sorted(glob.glob("data/*-bookTicker-*.csv")):
    d=pd.read_csv(f,usecols=["best_bid_price","best_bid_qty","best_ask_price","best_ask_qty","transaction_time"],
                  dtype={"best_bid_price":"float64","best_bid_qty":"float64","best_ask_price":"float64","best_ask_qty":"float64","transaction_time":"int64"})
    d=d.sort_values("transaction_time",kind="stable")
    np.savez(f.replace(".csv",".npz"),bp=d.best_bid_price.values,bq=d.best_bid_qty.values,ap=d.best_ask_price.values,aq=d.best_ask_qty.values,t=d.transaction_time.values)
    print(f, len(d))
for f in sorted(glob.glob("data/*-aggTrades-*.csv")):
    d=pd.read_csv(f,usecols=["price","quantity","transact_time","is_buyer_maker"])
    np.savez(f.replace(".csv",".npz"),p=d.price.values,q=d.quantity.values,t=d.transact_time.values,sell=d.is_buyer_maker.values.astype(bool))
    print(f,len(d))
