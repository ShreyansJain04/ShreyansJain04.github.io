import datetime as dt, pathlib, subprocess, concurrent.futures as cf, time, glob
out = pathlib.Path("data/bhav")
days = sorted(dt.datetime.strptime(pathlib.Path(f).stem,"%Y%m%d").date() for f in glob.glob("data/ind_close/*.csv"))
def urls(d):
    old = f"https://archives.nseindia.com/content/historical/EQUITIES/{d:%Y}/{d.strftime('%b').upper()}/cm{d:%d}{d.strftime('%b').upper()}{d:%Y}bhav.csv.zip"
    new = f"https://archives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
    return [new, old] if d >= dt.date(2024,7,1) else [old, new]
def get(d):
    f = out/f"{d:%Y%m%d}.zip"
    if f.exists() and f.stat().st_size > 5000: return "skip"
    for u in urls(d):
        for _ in range(2):
            r = subprocess.run(["curl","-s","--max-time","30","-A","Mozilla/5.0","-w","%{http_code}","-o",str(f),u],capture_output=True,text=True)
            if r.stdout.strip()=="200" and f.stat().st_size>5000: return "ok"
            if r.stdout.strip()=="404": break
            time.sleep(2)
    f.unlink(missing_ok=True); return "fail"
with cf.ThreadPoolExecutor(5) as ex: res=list(ex.map(get, days))
from collections import Counter; print(Counter(res))
