# Overnight vs market-hours returns on NSE

Code for the blog post "Nifty made all its money while the market was closed".
Run from this folder, in order (Python 3, pandas, matplotlib):

1. `python fetch_ind.py`  – NSE daily index files → `data/ind_close/`
2. `python fetch_bhav.py` – NSE daily equity bhavcopies → `data/bhav/` (~260 MB)
3. `python build_index.py` and `python parse_bhav.py`
4. `python idx_split.py`, `python stock_level.py`, `python gap_quintiles.py`
5. `python overnight_figs.py` – writes the charts to `figs/`

Data is public NSE archives, Jan 2016 – Nov 2026. Educational only; not investment advice.
