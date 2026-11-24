import datetime as dt, pathlib, subprocess, concurrent.futures as cf, time
out = pathlib.Path("data/ind_close")
d = dt.date(2016,1,1); end = dt.date(2026,11,24); days=[]
while d <= end:
    if d.weekday() < 5: days.append(d)
    d += dt.timedelta(days=1)
def get(d):
    f = out/f"{d:%Y%m%d}.csv"
    if f.exists() and f.stat().st_size > 1000: return "skip"
    url = f"https://archives.nseindia.com/content/indices/ind_close_all_{d:%d%m%Y}.csv"
    for _ in range(2):
        r = subprocess.run(["curl","-s","--max-time","20","-A","Mozilla/5.0","-w","%{http_code}","-o",str(f),url],capture_output=True,text=True)
        code = r.stdout.strip()
        if code == "200" and f.stat().st_size > 1000: return "ok"
        if code == "404":
            f.unlink(missing_ok=True); return "404"
        time.sleep(2)
    f.unlink(missing_ok=True); return code
with cf.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(get, days))
from collections import Counter; print(Counter(res))
