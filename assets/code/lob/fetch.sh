#!/bin/sh
# Download Binance USD-M futures top-of-book updates and aggregated trades (public data.binance.vision)
mkdir -p data && cd data
for s in BTCUSDT ETHUSDT; do for d in 2024-03-26 2024-03-27; do for k in bookTicker aggTrades; do
  curl -sO https://data.binance.vision/data/futures/um/daily/$k/$s/$s-$k-$d.zip && unzip -oq $s-$k-$d.zip
done; done; done
