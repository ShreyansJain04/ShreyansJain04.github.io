# Intraday return by overnight-gap quintile, 100 most-traded stocks, Jan 2016 - 19 Nov 2024
import pandas as pd
a=pd.read_pickle("data/bhav_all.pkl"); a=a[a.ser=="EQ"]
a=a[(a.o>0)&(a.c>0)&(a.pc>0)&(a.o<=a.h*1.0001)&(a.o>=a.l*0.9999)]
a["on"]=a.o/a.pc-1; a["id"]=a.c/a.o-1
a=a[(a.on.abs()<0.2)&(a.id.abs()<0.2)].sort_values(["sym","date"])
a["adv"]=a.groupby("sym").val.transform(lambda s:s.rolling(60,min_periods=40).mean().shift(1))
a["rk"]=a.groupby("date").adv.rank(ascending=False)
x=a[(a.rk<=100)&(a.date<"2024-11-20")].copy()
x["q"]=x.groupby("date").on.transform(lambda s: pd.qcut(s.rank(method="first"),5,labels=False))
r=x.groupby("q")[["on","id"]].mean()*1e4
r.to_pickle("data/gap_quintiles.pkl"); print(r.round(1)); print(len(x),"stock-days")
