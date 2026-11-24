# Queue imbalance vs direction of the next mid-price move; fit hidden-queue k on day 1, test on day 2
import numpy as np, pandas as pd
from scipy.optimize import minimize_scalar
TICK={"BTCUSDT":0.1,"ETHUSDT":0.01}; out={}
for sym in ["BTCUSDT","ETHUSDT"]:
    parts=[]
    for d in ["2024-03-26","2024-03-27"]:
        z=np.load(f"data/{sym}-bookTicker-{d}.npz"); tk=TICK[sym]
        bp,bq,ap,aq,t=z["bp"],z["bq"],z["ap"],z["aq"],z["t"]
        mid=np.rint((bp+ap)/tk).astype(np.int64); spr=np.rint((ap-bp)/tk).astype(np.int64)
        chg=np.flatnonzero(np.diff(mid)!=0)+1; nxt=np.searchsorted(chg,np.arange(len(mid)),side="right"); valid=nxt<len(chg)
        nidx=np.where(valid,chg[np.minimum(nxt,len(chg)-1)],0); up=mid[nidx]>mid
        sec=t//1000; last=np.flatnonzero(np.r_[sec[1:]!=sec[:-1],True])
        s=last[(spr[last]==1)&valid[last]&(bq[last]>0)&(aq[last]>0)]
        parts.append(pd.DataFrame({"bq":bq[s],"aq":aq[s],"up":up[s],"day":d,"wait":(t[nidx[s]]-t[s])/1000}))
    df=pd.concat(parts); df["I"]=df.bq/(df.bq+df.aq); out[sym]=df
    d1=df[df.day=="2024-03-26"]; d2=df[df.day=="2024-03-27"]
    model=lambda x,k: 1-(2/np.pi)*np.arctan((x.aq+k)/(x.bq+k)); br=lambda x,p: np.mean((p-x.up)**2)
    k=minimize_scalar(lambda k: br(d1,model(d1,k)),bounds=(0,50),method="bounded").x; out[sym+"_k"]=k
    print(sym,len(df),"samples, median wait %.2fs; k=%.2f, median queue %.2f"%(df.wait.median(),k,np.median(np.r_[d1.bq,d1.aq])))
    for name,p in [("coin",np.full(len(d2),0.5)),("model k=0",model(d2,0)),("model + k",model(d2,k))]:
        print(f"   day2 {name:10s} brier {br(d2,p):.4f} hit {np.mean((p>0.5)==d2.up):.3f}")
pd.to_pickle(out,"data/qimb_raw.pkl")
