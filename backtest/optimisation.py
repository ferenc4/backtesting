import time

from backtest.bt import BuyAsapHoldStrategy, Backtest
from backtest.rates import InMemoryRatesCollection
from backtest.sample_data import sample_growth_data


def optimisation_test(sample_size=1, worker_count_options: [] = None):
    if worker_count_options is None:
        worker_count_options = []
    run_duration = 100
    rc = InMemoryRatesCollection.from_list(sample_growth_data(run_duration * 3))
    bt = Backtest(rc=rc, strategy_supplier=BuyAsapHoldStrategy, duration_days=run_duration)
    time_sums = dict()
    print(f"Evaluating worker count options between {worker_count_options}")
    for sample_index in range(0, sample_size):
        for worker_count in worker_count_options:
            start = time.time()
            bt.run(worker_count)
            end = time.time()
            existing_time_sum = time_sums.get(worker_count, 0)
            time_sums[worker_count] = existing_time_sum + end - start

    recommended_workers = None
    best_time = None
    for worker_count, time_sum in time_sums.items():
        avg_time = time_sum / sample_size
        print(f"Worker count <{worker_count}> Average duration <{avg_time}>")
        if best_time is None or avg_time < best_time:
            best_time = avg_time
            recommended_workers = worker_count
    print("Recommended number of workers:", recommended_workers)
