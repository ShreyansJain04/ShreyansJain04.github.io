import pandas as pd, numpy as np
a=pd.read_pickle("data/bhav_all.pkl"); a=a[a.ser=="EQ"]
a=a[(a.o>0)&(a.c>0)&(a.pc>0)&(a.h>=a.l)]
a=a[(a.o<=a.h*1.0001)&(a.o>=a.l*0.9999)]
a["on"]=a.o/a.pc-1; a["id"]=a.c/a.o-1
a=a[(a.on.abs()<0.2)&(a.id.abs()<0.2)].sort_values(["sym","date"])
a["adv"]=a.groupby("sym").val.transform(lambda s:s.rolling(60,min_periods=40).mean().shift(1))
a["rk"]=a.groupby("date").adv.rank(ascending=False)
t=a[a.rk<=100].groupby("date").agg(on=("on","mean"),id=("id","mean"),fpos=("on",lambda x:(x>0).mean()),n=("on","size"))
t=t[t.n>=90]
t.to_pickle("data/top100_daily.pkl")
COST=3.5e-4
t["short_id_net"]=-t.id-COST
for y,g in t.groupby(t.index.year):
    s=g.short_id_net
    print(y,len(g),"on %.1f id %.1f bp | %%stocks gap up %.0f%% | short-intraday net %.1f bp/day, ann Sharpe %.1f, cum %+.0f%%"%(g.on.mean()*1e4,g.id.mean()*1e4,g.fpos.mean()*100,s.mean()*1e4,s.mean()/s.std()*np.sqrt(250),((1+s).prod()-1)*100))
for lab,m in [("pre SEBI 2024-11-20",t.index<"2024-11-20"),("2024-11-20..2026-08-02",(t.index>="2024-11-20")&(t.index<"2026-08-03")),("CAS from 2026-08-03",t.index>="2026-08-03")]:
    g=t[m]; print(lab,len(g),"on %.1f id %.1f net short %.1f"%(g.on.mean()*1e4,g.id.mean()*1e4,g.short_id_net.mean()*1e4))
