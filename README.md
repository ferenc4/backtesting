# backtesting
## Prerequisites
```
source venv/bin/activate
```
## To execute simulation
```
python -m backtest -w <INSERT NUMBER OF WORKERS HERE e.g. 1>
```
## To optimise
```
python -m backtest -o <INSERT WORKER COUNTS TO TRY e.g. 1 2 4 8 16>
```
### Commonly used functions
To plot the price of an asset
```
rc: RatesCollection = from_fmp_api("AAPL")
rc.plot()
```
