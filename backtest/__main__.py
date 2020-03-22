import argparse

from backtest.bt import run
from backtest.optimisation import optimisation_test


def to_int_array(str_ary: [str]):
    return [int(v) for v in str_ary]


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-o", "--optimise", help="find and print the optimal number of workers from the entered list",
                       nargs='+')
    group.add_argument("-w", "--workers", help="run calculations with number of workers")
    args = parser.parse_args()
    parser.parse_args()
    if args.optimise is not None:
        int_array = to_int_array(args.optimise)
        optimisation_test(sample_size=3, worker_count_options=int_array)
    elif args.workers is not None:
        worker_count = int(args.workers)
        run(worker_count)


if __name__ == "__main__":
    main()
