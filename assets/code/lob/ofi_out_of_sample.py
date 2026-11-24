import numpy as np, pandas as pd
exec(open("ofi.py").read().split("rows=[]")[0])
def buckets(sym,d,dt=10):
    z,tr=load(sym,d); tk=TICK[sym]; bp,bq,ap,aq,t=z["bp"],z["bq"],z["ap"],z["aq"],z["t"]
    e=np.zeros_like(bq); e[1:]=(bp[1:]>=bp[:-1])*bq[1:]-(bp[1:]<=bp[:-1])*bq[:-1]-(ap[1:]<=ap[:-1])*aq[1:]+(ap[1:]>=ap[:-1])*aq[:-1]
    df=pd.DataFrame({"b":t//(dt*1000),"e":e,"mid":(bp+ap)/2/tk,"dep":(bq+aq)/2})
    g=df.groupby("b").agg(ofi=("e","sum"),mid=("mid","last"),dep=("dep","mean"))
    g=g.reindex(range(g.index.min(),g.index.max()+1)); g["mid"]=g.mid.ffill(); g["ofi"]=g.ofi.fillna(0); g["dep"]=g.dep.ffill(); g["dp"]=g.mid.diff()
    ti=pd.Series(np.where(tr["sell"],-tr["q"],tr["q"])).groupby(tr["t"]//(dt*1000)).sum(); g["ti"]=ti.reindex(g.index).fillna(0)
    g=g.dropna(); g["w"]=(g.index*dt)//1800
    g["wdep"]=g.groupby("w").dep.transform("mean")
    return g
out={}
for sym in ["BTCUSDT","ETHUSDT"]:
    g1=buckets(sym,"2024-03-26"); g2=buckets(sym,"2024-03-27")
    # one-parameter model dp = c * ofi / depth(window), fit day1, test day2
    x1=g1.ofi/g1.wdep; c=(x1*g1.dp).sum()/(x1*x1).sum()
    x2=g2.ofi/g2.wdep; pred=c*x2; r2=1-((g2.dp-pred)**2).sum()/((g2.dp-g2.dp.mean())**2).sum()
    # TI added on top of OFI (day2, pooled, scaled)
    X=np.column_stack([np.ones(len(g2)),x2,g2.ti/g2.wdep]); b=np.linalg.lstsq(X,g2.dp.values,rcond=None)[0]; res=g2.dp.values-X@b
    r2both=1-res.var()/g2.dp.var()
    X1=np.column_stack([np.ones(len(g2)),x2]); b1=np.linalg.lstsq(X1,g2.dp.values,rcond=None)[0]; r2o=1-(g2.dp.values-X1@b1).var()/g2.dp.var()
    Xt=np.column_stack([np.ones(len(g2)),g2.ti/g2.wdep]); bt=np.linalg.lstsq(Xt,g2.dp.values,rcond=None)[0]; r2t=1-(g2.dp.values-Xt@bt).var()/g2.dp.var()
    print(sym,"c=%.3f  out-of-sample R2 (day2, one parameter from day1) = %.3f | day2 pooled in-sample: OFI %.3f, TI %.3f, both %.3f | n=%d"%(c,r2,r2o,r2t,r2both,len(g2)))
    out[sym]=(g1,g2,c)
pd.to_pickle(out,"data/ofi_buckets.pkl")
