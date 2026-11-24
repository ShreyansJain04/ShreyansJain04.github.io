import pandas as pd, numpy as np
BAD=pd.to_datetime(["2023-06-04","2023-10-04","2023-11-04"])
n=pd.read_pickle("data/ind_all.pkl"); n=n[~n.date.isin(BAD)]; n["u"]=n.name.str.upper()
names={"NIFTY 50":"Nifty 50","NIFTY BANK":"Nifty Bank","NIFTY MIDCAP 100":"Nifty Midcap 100","NIFTY SMALLCAP 100":"Nifty Smallcap 100","NIFTY NEXT 50":"Nifty Next 50"}
out={}
for k,v in names.items():
    x=n[n.u==k].sort_values("date").copy(); x["pc"]=x.c.shift(); x["pd"]=x.date.shift(); x=x.dropna()
    x["on"]=x.o/x.pc-1; x["id"]=x.c/x.o-1; x["gap"]=(x.date-x.pd).dt.days; x=x[x.gap<=6]; out[v]=x
    pre=x[x.date<"2024-11-20"]; post=x[x.date>="2024-11-20"]
    t=lambda s: s.mean()/s.std()*np.sqrt(len(s))
    print(f"{v:20s} start {x.date.min().date()} cum on {(1+x.on).prod():.2f}x id {(1+x.id).prod():.3f}x tot {(x.c/x.pc).prod():.2f}x | pre on {pre.on.mean()*1e4:.1f} (t={t(pre.on):.1f}) id {pre.id.mean()*1e4:.1f} (t={t(pre.id):.1f}) | post on {post.on.mean()*1e4:.1f} id {post.id.mean()*1e4:.1f} | frac on>0 pre {(pre.on>0).mean():.2f}")
pd.to_pickle(out,"data/idx_split.pkl")
x=out["Nifty 50"]; pre=x[x.date<"2024-11-20"]
print(pre.groupby(pre.gap.clip(upper=4)).on.agg(["mean","count"]))
