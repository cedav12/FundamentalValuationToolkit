import argparse
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument("--tickers", nargs="+", type=str, help="list of tickers to be analyzed")

def main(args: argparse.Namespace):
    for ticker in args.tickers:
        print(ticker)


if __name__ == "__main__":
    # Parse arguments
    arg = parser.parse_args([] if "__file__" not in globals() else None)
    main(arg)