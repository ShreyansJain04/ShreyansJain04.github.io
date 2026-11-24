# Combine NSE daily index files (data/ind_close/*.csv) into data/ind_all.pkl
import pandas as pd, glob
fr=[]
for f in sorted(glob.glob("data/ind_close/*.csv")):
    d=pd.read_csv(f); d.columns=[c.strip() for c in d.columns]; fr.append(d)
df=pd.concat(fr)
df["name"]=df["Index Name"].str.strip()
df["date"]=pd.to_datetime(df["Index Date"].str.strip(),format="%d-%m-%Y",errors="coerce")
for c,n in [("Open Index Value","o"),("High Index Value","h"),("Low Index Value","l"),("Closing Index Value","c")]:
    df[n]=pd.to_numeric(df[c],errors="coerce")
df=df[["name","date","o","h","l","c"]].dropna(subset=["date","c"]).drop_duplicates(["name","date"])
df.to_pickle("data/ind_all.pkl"); print(df.date.min(), df.date.max(), df.name.nunique(), "indices")
