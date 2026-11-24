# Order-book posts: order flow imbalance and queue imbalance

Code for "One number explains 70% of short-term price moves" and "Will the next tick be up?".
Run from this folder (Python 3, numpy, pandas, scipy, matplotlib):

1. `sh fetch.sh` – about 0.9 GB of zips from data.binance.vision, ~7 GB unzipped
2. `python prep.py` – CSV → compact .npz
3. `python ofi.py` and `python ofi_out_of_sample.py`
4. `python queue_imbalance.py`
5. `python figs.py` – charts to `figs/`
