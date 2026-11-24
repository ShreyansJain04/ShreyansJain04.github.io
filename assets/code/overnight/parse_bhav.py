import pandas as pd, glob, zipfile, pathlib
rows=[]
for f in sorted(glob.glob("data/bhav/*.zip")):
    d=pathlib.Path(f).stem
    with zipfile.ZipFile(f) as z:
        df=pd.read_csv(z.open(z.namelist()[0]))
    df.columns=[c.strip() for c in df.columns]
    if "SYMBOL" in df.columns:
        df=df.rename(columns={"SYMBOL":"sym","SERIES":"ser","OPEN":"o","HIGH":"h","LOW":"l","CLOSE":"c","PREVCLOSE":"pc","TOTTRDVAL":"val","TOTTRDQTY":"vol"})
    else:
        df=df.rename(columns={"TckrSymb":"sym","SctySrs":"ser","OpnPric":"o","HghPric":"h","LwPric":"l","ClsPric":"c","PrvsClsgPric":"pc","TtlTrfVal":"val","TtlTradgVol":"vol"})
    df=df[["sym","ser","o","h","l","c","pc","val","vol"]]
    df=df[df.ser.astype(str).str.strip().isin(["EQ","BE"])]
    df["date"]=pd.Timestamp(d); rows.append(df)
a=pd.concat(rows); a["sym"]=a.sym.str.strip(); a["ser"]=a.ser.str.strip()
a.to_pickle("data/bhav_all.pkl"); print(a.shape, a.date.min(), a.date.max())
