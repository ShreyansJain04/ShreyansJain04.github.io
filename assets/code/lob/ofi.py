import numpy as np, pandas as pd, sys
TICK={"BTCUSDT":0.1,"ETHUSDT":0.01}
def load(sym,d):
    z=np.load(f"data/{sym}-bookTicker-{d}.npz"); tr=np.load(f"data/{sym}-aggTrades-{d}.npz")
    return z,tr
def ols(y,x):
    X=np.column_stack([np.ones_like(x),x]); b=np.linalg.lstsq(X,y,rcond=None)[0]; r=y-X@b
    return b, 1-r.var()/y.var()
rows=[]
for sym in ["BTCUSDT","ETHUSDT"]:
    for d in ["2024-03-26","2024-03-27"]:
        z,tr=load(sym,d); tk=TICK[sym]
        bp,bq,ap,aq,t=z["bp"],z["bq"],z["ap"],z["aq"],z["t"]
        spr=np.rint((ap-bp)/tk)
        if d=="2024-03-26": print(sym,"spread ticks dist",{int(k):round(v,4) for k,v in pd.Series(spr).value_counts(normalize=True).head(4).items()}, "median depth L1 (coins)", np.median((bq+aq)/2))
        e=np.zeros_like(bq)
        e[1:]=(bp[1:]>=bp[:-1])*bq[1:]-(bp[1:]<=bp[:-1])*bq[:-1]-(ap[1:]<=ap[:-1])*aq[1:]+(ap[1:]>=ap[:-1])*aq[:-1]
        mid=(bp+ap)/2/tk
        for dt in [1,10,60]:
            b=(t//(dt*1000)); 
            df=pd.DataFrame({"b":b,"e":e,"mid":mid,"dep":(bq+aq)/2})
            g=df.groupby("b").agg(ofi=("e","sum"),mid=("mid","last"),dep=("dep","mean"))
            g=g.reindex(range(g.index.min(),g.index.max()+1)); g["mid"]=g.mid.ffill(); g["ofi"]=g.ofi.fillna(0); g["dep"]=g.dep.ffill()
            g["dp"]=g.mid.diff()
            tb=(tr["t"]//(dt*1000)); ti=pd.Series(np.where(tr["sell"],-tr["q"],tr["q"])).groupby(tb).sum()
            g["ti"]=ti.reindex(g.index).fillna(0)
            g=g.dropna(); g["w"]=(g.index*dt)//1800
            for w,x in g.groupby("w"):
                if len(x)<20: continue
                bo,r2o=ols(x.dp.values,x.ofi.values); bt,r2t=ols(x.dp.values,x.ti.values)
                rows.append(dict(sym=sym,d=d,dt=dt,w=w,beta=bo[1],r2_ofi=r2o,r2_ti=r2t,dep=x.dep.mean(),n=len(x),sd_dp=x.dp.std()))
r=pd.DataFrame(rows); r.to_pickle("data/ofi_windows.pkl")
print(r.groupby(["sym","dt"])[["r2_ofi","r2_ti"]].median().round(3))
x=r[r.dt==10]
for sym,g in x.groupby("sym"):
    s,c=np.polyfit(np.log(g.dep),np.log(g.beta),1); print(sym,"log beta vs log depth slope %.2f; median beta*depth %.3f"%(s,np.median(g.beta*g.dep)))
