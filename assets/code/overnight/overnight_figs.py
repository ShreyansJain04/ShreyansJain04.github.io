import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates
import os; OUT="figs/"; os.makedirs(OUT,exist_ok=True)
BLUE,ORANGE,GRAY,INK,INK2="#2a78d6","#eb6834","#8a8985","#0b0b0b","#52514e"
plt.rcParams.update({"font.size":12,"axes.edgecolor":"#c9c8c4","axes.labelcolor":INK2,"xtick.color":INK2,"ytick.color":INK2,
  "axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.color":"#ebeae6","grid.linewidth":0.8,"figure.facecolor":"#fcfcfb","axes.facecolor":"#fcfcfb","savefig.facecolor":"#fcfcfb","lines.linewidth":2,"axes.axisbelow":True})
src="Source: NSE daily index and bhavcopy files, Jan 2016 – Nov 2026. Price returns, no dividends."
idx=pd.read_pickle("data/idx_split.pkl")
n=idx["Nifty 50"].set_index("date")
# Fig 1 headline
fig,ax=plt.subplots(figsize=(11,6))
tot=(n.c/n.pc).cumprod(); on=(1+n.on).cumprod(); idr=(1+n.id).cumprod()
ax.plot(on.index,on*100,color=BLUE,label="Overnight only (close → next open)")
ax.plot(tot.index,tot*100,color=GRAY,label="Buy and hold")
ax.plot(idr.index,idr*100,color=ORANGE,label="Market hours only (open → close)")
ax.set_yscale("log"); ax.set_yticks([10,20,50,100,200,500,1000,2000]); ax.set_yticklabels(["10","20","50","100","200","500","1,000","2,000"])
for s,c in [(on,BLUE),(tot,GRAY),(idr,ORANGE)]:
    ax.annotate(f"₹{s.iloc[-1]*100:,.0f}",(s.index[-1],s.iloc[-1]*100),xytext=(6,0),textcoords="offset points",va="center",color=INK,fontsize=12,fontweight="bold")
ax.set_ylabel("Value of ₹100 invested in Jan 2016 (log scale)")
ax.set_title("Nifty 50: every rupee of the last decade was made while the market was closed",loc="left",fontsize=15,color=INK,pad=14)
ax.legend(frameon=False,loc="upper left"); ax.set_xlim(on.index[0],on.index[-1]+pd.Timedelta(days=330)); ax.set_xticks(pd.to_datetime([f"{y}-01-01" for y in range(2016,2027,2)])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
fig.text(0.01,0.01,src,fontsize=9,color=INK2); fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(OUT+"fig1-nifty-split.png",dpi=150); plt.close()
# Fig 2 by index
rows=[]
for k in ["Nifty 50","Nifty Bank","Nifty Next 50","Nifty Midcap 100","Nifty Smallcap 100"]:
    x=idx[k]; x=x[(x.on.abs()<0.1)&(x.date<"2024-11-20")]; rows.append((k,x.on.mean()*1e4,x.id.mean()*1e4))
fig,ax=plt.subplots(figsize=(11,5.2)); y=np.arange(len(rows)); h=0.36
ax.barh(y-h/2-0.01,[r[1] for r in rows],h,color=BLUE,label="Overnight"); ax.barh(y+h/2+0.01,[r[2] for r in rows],h,color=ORANGE,label="Market hours")
for i,r in enumerate(rows):
    ax.text(r[1]+0.6,i-h/2,f"+{r[1]:.1f}",va="center",color=INK,fontsize=11); ax.text(r[2]-0.6,i+h/2,f"{r[2]:.1f}",va="center",ha="right",color=INK,fontsize=11)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows]); ax.invert_yaxis(); ax.axvline(0,color=INK2,lw=1)
ax.set_xlabel("Average return per day, basis points"); ax.set_xlim(-28,38)
ax.set_title("The smaller the stocks, the bigger the split (Jan 2016 – Nov 2024)",loc="left",fontsize=15,color=INK,pad=14)
ax.legend(frameon=False,loc="upper right"); ax.grid(axis="y",visible=False)
fig.text(0.01,0.01,"Source: NSE daily index files. Gaps in the index files longer than 6 days are skipped.",fontsize=9,color=INK2); fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(OUT+"fig2-by-index.png",dpi=150); plt.close()
# Fig 3 nights closed
pre=n[n.index<"2024-11-20"].copy(); pre["g"]=pre.gap.map(lambda d:"1 night\n(Tue–Fri)" if d==1 else ("Weekend\n(3 nights)" if d==3 else None))
g=pre.dropna(subset=["g"]).groupby("g").on.agg(["mean","std","count"]); g["se"]=g["std"]/np.sqrt(g["count"])
order=["1 night\n(Tue–Fri)","Weekend\n(3 nights)"]; g=g.loc[order]
fig,ax=plt.subplots(figsize=(8,5.2))
ax.set_axisbelow(True); ax.bar([0,1],g["mean"]*1e4,0.5,color=BLUE,yerr=1.96*g["se"]*1e4,capsize=6,ecolor=INK2)
ax.bar([1.62],[g["mean"].iloc[0]*1e4*3],0.42,color="none",edgecolor=GRAY,lw=1.5,ls="--")
ax.text(1.62,g["mean"].iloc[0]*1e4*3+1,"If it were pay\nfor holding risk:\n~3× one night",ha="center",va="bottom",color=INK2,fontsize=10)
for i,v in enumerate(g["mean"]*1e4): ax.text(i+0.29,v,f"{v:.1f} bp",va="center",color=INK,fontsize=12,fontweight="bold")
ax.set_xticks([0,1]); ax.set_xticklabels(order); ax.set_ylabel("Nifty 50 average overnight return, bp"); ax.set_ylim(0,52); ax.set_xlim(-0.5,2.0)
ax.set_title("Three nights closed earn no more than one",loc="left",fontsize=15,color=INK,pad=14); ax.grid(axis="x",visible=False)
fig.text(0.01,0.01,"Nifty 50, Jan 2016 – Nov 2024. Error bars: 95% confidence interval. Holiday gaps excluded.",fontsize=9,color=INK2); fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(OUT+"fig3-weekend.png",dpi=150); plt.close()
print(g)
# Fig 4 gap quintile reversal (top 100 stocks)
q=pd.read_pickle("data/gap_quintiles.pkl")
fig,ax=plt.subplots(figsize=(10,5.2)); xx=np.arange(5); w=0.36
ax.bar(xx-w/2-0.01,q.on,w,color=BLUE,label="Overnight gap"); ax.bar(xx+w/2+0.01,q.id,w,color=ORANGE,label="Same day, open → close")
for i,(o,d) in enumerate(zip(q.on,q.id)):
    ax.text(i-w/2,o+(3 if o>0 else -3),f"{o:+.0f}",ha="center",va="bottom" if o>0 else "top",fontsize=10,color=INK)
    ax.text(i+w/2,d+(3 if d>0 else -3),f"{d:+.0f}",ha="center",va="bottom" if d>0 else "top",fontsize=10,color=INK)
ax.axhline(0,color=INK2,lw=1); ax.set_xticks(xx); ax.set_xticklabels(["Biggest\ngap down","2","3","4","Biggest\ngap up"])
ax.set_ylabel("Average return, bp"); ax.set_ylim(-85,125); ax.legend(frameon=False,loc="upper left"); ax.grid(axis="x",visible=False)
ax.set_title("Gaps fade, and even an average open is sold",loc="left",fontsize=15,color=INK,pad=14)
fig.text(0.01,0.01,"100 most-traded NSE stocks each day (trailing 60-day value), sorted daily into fifths by overnight gap. Jan 2016 – Nov 2024, 215k stock-days.",fontsize=9,color=INK2)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(OUT+"fig4-gap-quintiles.png",dpi=150); plt.close()
# Fig 5 rolling Nifty with regime lines
r=n[["on","id"]].rolling(250).mean()*1e4
fig,ax=plt.subplots(figsize=(11,5.2))
ax.plot(r.index,r.on,color=BLUE,label="Overnight"); ax.plot(r.index,r.id,color=ORANGE,label="Market hours"); ax.axhline(0,color=INK2,lw=1)
for d,t in [("2024-11-20","SEBI F&O curbs\n20 Nov 2024"),("2026-08-03","Closing auction\n3 Aug 2026")]:
    ax.axvline(pd.Timestamp(d),color=GRAY,ls="--",lw=1.2); ax.text(pd.Timestamp(d)-pd.Timedelta(days=20),23,t,ha="right",va="top",fontsize=10,color=INK2)
ax.set_ylabel("Trailing 1-year average, bp per day"); ax.set_ylim(-18,30); ax.legend(frameon=False,loc="lower left")
ax.set_title("Nifty 50: the overnight edge faded through 2025",loc="left",fontsize=15,color=INK,pad=14)
fig.text(0.01,0.01,src,fontsize=9,color=INK2); fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(OUT+"fig5-rolling.png",dpi=150); plt.close()
# Fig 6 ETF opening premium
a=pd.read_pickle("data/bhav_all.pkl")
fig,ax=plt.subplots(figsize=(11,5.2))
for s,refn,col in [("NIFTYBEES","Nifty 50",BLUE),("BANKBEES","Nifty Bank",ORANGE),("JUNIORBEES","Nifty Next 50","#1baf7a")]:
    b=a[(a.sym==s)&(a.o>0)].set_index("date").sort_index(); ref=idx[refn].set_index("date")
    m=b.join(ref[["on"]],how="inner"); m["prem"]=(m.o/m.pc)/(1+m.on)-1
    y=m.groupby(m.index.year).prem.median()*1e4
    ax.plot(y.index,y.values,marker="o",ms=8,color=col,label=f"{s} vs {refn}")
    ax.annotate(f"{y.iloc[-1]:.0f} bp",(y.index[-1],y.iloc[-1]),xytext=(8,{"NIFTYBEES":7,"BANKBEES":-7}.get(s,0)),textcoords="offset points",va="center",fontsize=11,color=INK)
ax.axhline(0,color=INK2,lw=1); ax.set_xticks(range(2016,2027)); ax.set_xlim(2015.6,2026.8)
ax.set_ylabel("Median opening premium, bp"); ax.legend(frameon=False,loc="upper left")
ax.set_title("Since 2020, index ETFs open well above where their index says they should",loc="left",fontsize=15,color=INK,pad=14)
fig.text(0.01,0.01,"Opening premium = ETF's open-vs-previous-close move minus its index's same move. Median by year. 2026 is Jan–Nov. Source: NSE bhavcopy and index files.",fontsize=9,color=INK2)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(OUT+"fig6-etf-premium.png",dpi=150); plt.close()
