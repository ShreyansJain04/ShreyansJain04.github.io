# Illustrative simulation of one parent order through a day (fictional stock "MRDN"). Not market data.
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng=np.random.default_rng(11)
BLUE,ORANGE,AQUA,GRAY,INK,INK2="#2a78d6","#eb6834","#1baf7a","#8a8985","#0b0b0b","#52514e"
plt.rcParams.update({"font.size":12,"axes.edgecolor":"#c9c8c4","axes.labelcolor":INK2,"xtick.color":INK2,"ytick.color":INK2,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.color":"#ebeae6","grid.linewidth":0.8,"figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","savefig.facecolor":"#fcfcfb","lines.linewidth":2,"axes.axisbelow":True})
import os; O="figs/"; os.makedirs(O,exist_ok=True)
T=390; t=np.arange(T)  # minutes after 9:30
ADV=6_000_000; Q=1_200_000; DECISION=84.00; LIMIT=85.00
u=1+1.3*np.exp(-t/30)+1.6*np.exp(-(T-1-t)/25); vol=ADV*0.88*u/u.sum()   # continuous-session volume; ~12% left for the close
# price path: Brownian bridge through anchors
anchors={0:84.18,11:84.21,110:84.45,240:84.62,350:85.00,389:85.10}
ks=sorted(anchors); p=np.zeros(T)
for a,b in zip(ks[:-1],ks[1:]):
    n=b-a; w=np.cumsum(rng.normal(0,0.035,n)); w=w-np.linspace(0,1,n)*w[-1]
    p[a:b]=np.linspace(anchors[a],anchors[b],n,endpoint=False)+w
p[-1]=anchors[389]; p=np.round(p,2)
ARR=11; BLOCK_T=110; BLOCK_Q=150_000
fills=np.zeros(T); fpx=np.zeros(T); remaining=Q
for i in range(ARR,T):
    if i==BLOCK_T:
        fills[i]+=BLOCK_Q; fpx[i]=p[i]; remaining-=BLOCK_Q  # midpoint block in a dark pool
    if p[i]>LIMIT: continue
    future=vol[i:].sum()+ADV*0.12
    target=remaining*vol[i]/future
    q=min(target*1.0,0.25*vol[i]); q=np.floor(q/100)*100
    if q<=0: continue
    impact=0.01+0.02*(q/vol[i])/0.2   # half-spread plus a little temporary impact, $/share
    px=p[i]+impact
    fpx[i]=(fpx[i]*fills[i]+px*q)/(fills[i]+q) if fills[i]>0 else px; fills[i]+=q; remaining-=q
filled=fills.sum(); avg=(fills*fpx).sum()/filled; close=p[-1]
dayvwap=(vol*p).sum()/vol.sum()
unf=Q-filled
delay=filled*(p[ARR]-DECISION); execu=filled*(avg-p[ARR]); opp=unf*(close-DECISION); base=Q*DECISION
print(f"filled {filled:,.0f} ({filled/Q:.1%}), avg {avg:.3f}, arrival {p[ARR]:.2f}, close {close:.2f}, day VWAP {dayvwap:.3f}")
print(f"IS total {(delay+execu+opp)/base*1e4:.1f}bp = delay {delay/base*1e4:.1f} + execution {execu/base*1e4:.1f} + opportunity {opp/base*1e4:.1f}")
print(f"vs VWAP: {(avg-dayvwap)/dayvwap*1e4:+.1f} bp (negative = beat VWAP for a buy); vs arrival {(avg-p[ARR])/p[ARR]*1e4:.1f} bp")
print("participation overall %.1f%%; last fill minute %d (%s)"%(filled/vol[ARR:].sum()*100, np.flatnonzero(fills)[-1], f"{9+(30+np.flatnonzero(fills)[-1])//60}:{(30+np.flatnonzero(fills)[-1])%60:02d}"))
pre=1.0*0.02*np.sqrt(Q/ADV)*1e4; print(f"pre-trade sqrt-law estimate {pre:.0f} bp")
np.savez("order_sim.npz",p=p,fills=fills,vol=vol)
# Figure: the day
lab=lambda m: f"{9+(30+m)//60}:{(30+m)%60:02d}"
fig,(a1,a2)=plt.subplots(2,1,figsize=(11,7.4),sharex=True,gridspec_kw={"height_ratios":[1.3,1]})
a1.plot(t,p,color=GRAY,lw=1.4,label="MRDN price"); a1.axhline(LIMIT,color=ORANGE,ls="--",lw=1.3); a1.text(5,LIMIT+0.02,"limit $85.00",color=ORANGE,fontsize=10)
a1.axhline(DECISION,color=INK2,ls=":",lw=1); a1.text(150,DECISION+0.02,"decision price $84.00 (yesterday's close)",color=INK2,fontsize=10)
fx=np.flatnonzero(fills); a1.scatter(fx,fpx[fx],s=np.clip(fills[fx]/800,4,260),color=BLUE,alpha=0.55,edgecolor="none",label="our fills (size ∝ quantity)")
for m,txt,dy in [(ARR,"9:41 order arrives\nat the broker",0.33),(BLOCK_T,"11:20 dark-pool\nblock, 150k shares",0.18),(334,"3:04 price breaks the\nlimit; algo mostly stops",-0.28)]:
    a1.annotate(txt,(m,p[m]),xytext=(m+8,p[m]+dy),fontsize=10,color=INK,arrowprops=dict(arrowstyle="-",color=INK2))
a1.set_ylabel("$ per share"); a1.legend(frameon=False,loc="lower right",fontsize=10)
a1.set_title("One order's day (illustrative simulation of a fictional stock)",loc="left",fontsize=15,color=INK,pad=12)
a2.bar(t,vol/1000,width=1,color=GRAY,alpha=0.45,label="market volume per minute")
a2.bar(t,fills/1000,width=1,color=BLUE,label="our fills per minute")
a2.set_ylim(0,max(vol.max(),8000)/1000*1.15); a2.text(110,a2.get_ylim()[1]*0.92,"block: 150k →",ha="right",fontsize=10,color=INK)
a2.set_ylabel("thousand shares"); a2.legend(frameon=False,loc="upper center",fontsize=10)
a2.set_xticks([0,30,90,150,210,270,330,389]); a2.set_xticklabels([lab(m) for m in [0,30,90,150,210,270,330,389]])
fig.text(0.01,0.01,"Simulated: U-shaped volume curve, VWAP-style schedule capped at 25% participation, one dark block, a limit price. Not market data.",fontsize=9,color=INK2)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(O+"fig2-the-day.png",dpi=150); plt.close()
# Figure: IS waterfall
parts=[("Delay\n(decision → arrival)",delay/base*1e4,GRAY),("Execution\n(arrival → fills)",execu/base*1e4,BLUE),("Opportunity\n(shares never bought)",opp/base*1e4,ORANGE)]
fig,ax=plt.subplots(figsize=(10,5)); c=0
for i,(n,v,col) in enumerate(parts):
    ax.bar(i,v,bottom=c,color=col,width=0.6); ax.text(i,c+v/2,f"{v:.1f} bp",ha="center",va="center",color="white",fontsize=12,fontweight="bold"); c+=v
ax.bar(3,c,color=INK,width=0.6); ax.text(3,c/2,f"{c:.1f} bp",ha="center",va="center",color="white",fontsize=12,fontweight="bold")
ax.set_xticks(range(4)); ax.set_xticklabels([x[0] for x in parts]+["Implementation\nshortfall"]); ax.set_ylabel("basis points of the decision value"); ax.grid(axis="x",visible=False)
ax.set_title("Where the 'paper' return went",loc="left",fontsize=15,color=INK,pad=12)
fig.text(0.01,0.01,"Same simulated order. Implementation shortfall measured against the price when the decision was made.",fontsize=9,color=INK2)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(O+"fig3-shortfall.png",dpi=150); plt.close()
