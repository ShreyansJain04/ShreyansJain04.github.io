import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
BLUE,ORANGE,AQUA,GRAY,INK,INK2="#2a78d6","#eb6834","#1baf7a","#8a8985","#0b0b0b","#52514e"
plt.rcParams.update({"font.size":12,"axes.edgecolor":"#c9c8c4","axes.labelcolor":INK2,"xtick.color":INK2,"ytick.color":INK2,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.color":"#ebeae6","grid.linewidth":0.8,"figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","savefig.facecolor":"#fcfcfb","lines.linewidth":2,"axes.axisbelow":True})
import os; O="figs/"; [os.makedirs(O+s,exist_ok=True) for s in ("ofi","queue")]
SRC="Source: Binance USDⓈ-M perpetual futures, best bid/ask updates and trades, 26–27 Mar 2024 (data.binance.vision)."
def foot(fig,t=SRC): fig.text(0.01,0.01,t,fontsize=9,color=INK2)
W=pd.read_pickle("data/ofi_windows.pkl"); B=pd.read_pickle("data/ofi_buckets.pkl")
# OFI fig1: one median window scatter BTC
g1=B["BTCUSDT"][0]; w10=W[(W.sym=="BTCUSDT")&(W.dt==10)&(W.d=="2024-03-26")]
wm=w10.iloc[(w10.r2_ofi-w10.r2_ofi.median()).abs().argsort().iloc[0]]
x=g1[g1.w==wm.w]
fig,axs=plt.subplots(1,2,figsize=(12,5.2),sharey=True)
for ax,col,lab,c in [(axs[0],"ofi","Order flow imbalance (BTC at the top of book)",BLUE),(axs[1],"ti","Trade imbalance (buy − sell volume, BTC)",ORANGE)]:
    ax.scatter(x[col],x.dp,s=14,color=c,alpha=0.55,edgecolor="none")
    b=np.polyfit(x[col],x.dp,1); xx=np.linspace(x[col].min(),x[col].max(),10); ax.plot(xx,np.polyval(b,xx),color=INK,lw=1.5)
    r2=np.corrcoef(x[col],x.dp)[0,1]**2; ax.text(0.04,0.93,f"R² = {r2:.2f}",transform=ax.transAxes,fontsize=14,fontweight="bold",color=INK)
    ax.set_xlabel(lab)
axs[0].set_ylabel("Mid-price change over 10 s, ticks")
fig.suptitle("Book events explain price moves far better than trades do",x=0.01,ha="left",fontsize=15,color=INK)
foot(fig,f"BTCUSDT perpetual, one 30-minute window on 26 Mar 2024 (the window with the median OFI R²), 10-second intervals. "+"Binance data.")
fig.tight_layout(rect=(0,0.03,1,0.95)); fig.savefig(O+"ofi/fig1-scatter.png",dpi=150); plt.close()
# OFI fig2: R2 distributions
fig,ax=plt.subplots(figsize=(11,5))
pos=0; ticks=[]; labs=[]
for sym in ["BTCUSDT","ETHUSDT"]:
    for col,c,name in [("r2_ofi",BLUE,"OFI"),("r2_ti",ORANGE,"Trades")]:
        v=W[(W.sym==sym)&(W.dt==10)][col]
        bp=ax.boxplot([v],positions=[pos],widths=0.55,patch_artist=True,showfliers=False,medianprops=dict(color=INK,lw=2))
        for p in bp["boxes"]: p.set_facecolor(c); p.set_alpha(0.85); p.set_edgecolor(c)
        ax.scatter(np.full(len(v),pos)+np.random.default_rng(0).uniform(-0.18,0.18,len(v)),v,s=10,color=INK,alpha=0.35,zorder=3)
        ax.text(pos+0.33,v.median(),f"{v.median():.2f}",va="center",fontsize=11,color=INK)
        ticks.append(pos); labs.append(f"{sym[:3]}\n{name}"); pos+=1
    pos+=0.6
ax.set_xticks(ticks); ax.set_xticklabels(labs); ax.set_ylabel("R² of 10 s mid-price changes"); ax.set_ylim(0,1); ax.grid(axis="x",visible=False)
ax.set_title("Across 96 half-hour windows per contract, OFI explains about twice as much",loc="left",fontsize=15,color=INK,pad=14)
foot(fig); fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(O+"ofi/fig2-r2.png",dpi=150); plt.close()
# OFI fig3: beta vs depth
fig,ax=plt.subplots(figsize=(10,5.4))
for sym,c in [("BTCUSDT",BLUE),("ETHUSDT",AQUA)]:
    v=W[(W.sym==sym)&(W.dt==10)]; s,i=np.polyfit(np.log(v.dep),np.log(v.beta),1)
    ax.scatter(v.dep,v.beta,s=28,color=c,alpha=0.8,edgecolor="none",label=f"{sym[:3]}: slope {s:.2f}")
    xx=np.geomspace(v.dep.min(),v.dep.max(),10); ax.plot(xx,np.exp(i)*xx**s,color=c,lw=1.5)
ax.set_xscale("log"); ax.set_yscale("log"); from matplotlib.ticker import FuncFormatter, LogLocator; [a.set_major_formatter(FuncFormatter(lambda v,_: f"{v:g}")) for a in (ax.xaxis,ax.yaxis)]; ax.xaxis.set_minor_formatter(FuncFormatter(lambda v,_: f"{v:g}" if str(v)[0] in "25" else "")); ax.set_xlabel("Average depth at the best quotes in the window (coins, log scale)"); ax.set_ylabel("Price impact β (ticks per coin, log scale)")
ax.legend(frameon=False,loc="upper right",title="fitted log-log slope (theory: −1)")
ax.set_title("Twice the depth, half the impact",loc="left",fontsize=15,color=INK,pad=14)
foot(fig); fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(O+"ofi/fig3-beta-depth.png",dpi=150); plt.close()
# Queue fig1: P(up) vs I, day2 out of sample
Q=pd.read_pickle("data/qimb_raw.pkl")
fig,axs=plt.subplots(1,2,figsize=(12,5.4),sharey=True)
for ax,sym in zip(axs,["BTCUSDT","ETHUSDT"]):
    df=Q[sym]; d2=df[df.day=="2024-03-27"].copy(); k=Q[sym+"_k"]
    d2["bin"]=pd.cut(d2.I,np.linspace(0,1,21),include_lowest=True); g=d2.groupby("bin",observed=True).agg(I=("I","mean"),p=("up","mean"))
    ii=np.linspace(0.005,0.995,200)
    ax.plot(ii,1-(2/np.pi)*np.arctan((1-ii)/ii),color=GRAY,ls="--",label="Random-walk model, visible queues only")
    med=np.median(np.r_[df.bq,df.aq]); 
    m2=d2.assign(p=1-(2/np.pi)*np.arctan((d2.aq+k)/(d2.bq+k))).groupby("bin",observed=True).p.mean()
    ax.plot(g.I,m2.values,color=BLUE,label=f"Same model + hidden queue k = {k:.1f} {sym[:3]}")
    ax.scatter(g.I,g.p,s=46,color=ORANGE,zorder=3,label="Observed, out of sample (27 Mar)")
    ax.plot([0,1],[0.5,0.5],color=INK2,lw=0.8); ax.set_xlabel("Queue imbalance  I = bid size / (bid + ask size)"); ax.set_title(sym,loc="left",fontsize=13,color=INK)
axs[0].set_ylabel("Probability the next mid move is up"); axs[0].legend(frameon=False,loc="upper left",fontsize=10)
fig.suptitle("The queues predict the next tick, but the market is less certain than the model",x=0.01,ha="left",fontsize=15,color=INK)
foot(fig,"k fitted on 26 Mar, tested on 27 Mar. States sampled once a second when the spread is one tick. Binance USDⓈ-M perpetuals.")
fig.tight_layout(rect=(0,0.03,1,0.95)); fig.savefig(O+"queue/fig1-pup.png",dpi=150); plt.close()
# Queue fig2: random walk in the quadrant schematic
fig,ax=plt.subplots(figsize=(6.4,6)); X0,Y0=9,6; found={"up":[],"down":[]}
for seed in range(400):
    r=np.random.default_rng(seed); x,y=[X0],[Y0]
    while x[-1]>0 and y[-1]>0 and len(x)<3000:
        dx,dy=[(1,0),(-1,0),(0,1),(0,-1)][r.integers(4)]; x.append(x[-1]+dx); y.append(y[-1]+dy)
    if max(x)>22 or max(y)>22 or len(x)<25: continue
    k="up" if y[-1]==0 else "down"
    if len(found[k])<(2 if k=="up" else 1): found[k].append((x,y))
    if len(found["up"])==2 and len(found["down"])==1: break
for (x,y),c in zip(found["up"]+found["down"],[BLUE,AQUA,ORANGE]):
    ax.plot(x,y,color=c,lw=1.3,alpha=0.9); ax.scatter([x[-1]],[y[-1]],color=c,s=55,zorder=3,clip_on=False)
ax.scatter([X0],[Y0],color=INK,s=60,zorder=4); ax.annotate(f"start: bid {X0}, ask {Y0}",(X0,Y0),xytext=(13,15),fontsize=11,color=INK,arrowprops=dict(arrowstyle="-",color=INK2))
ax.set_xlim(0,24); ax.set_ylim(0,24); ax.set_xlabel("Bid queue size"); ax.set_ylabel("Ask queue size")
ax.text(23.5,0.5,"ask empties first → price ticks UP",ha="right",va="bottom",fontsize=10,color=INK)
ax.text(0.5,23.5,"bid empties first → DOWN",rotation=90,ha="left",va="top",fontsize=10,color=INK)
p_up=1-(2/np.pi)*np.arctan(Y0/X0)
ax.text(13,19,f"P(up) = 1 − (2/π)·arctan(ask/bid)\n          = {p_up:.2f}",fontsize=11,color=INK)
ax.set_title("The next tick is a race between two queues",loc="left",fontsize=13,color=INK,pad=12)
fig.tight_layout(); fig.savefig(O+"queue/fig2-race.png",dpi=150); plt.close()
print("ok")
