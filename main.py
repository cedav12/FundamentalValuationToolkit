import argparse
from data.pipeline import AnalysisPipeline

parser = argparse.ArgumentParser()

parser.add_argument("--tickers", nargs="+", type=str, required=True, help="list of tickers to be analyzed")
parser.add_argument("--output_path", default="output_reports", type=str,
                    help="Specify path, where output will be saved. If None, no output will be saved")

def main(args: argparse.Namespace):
    pipeline = AnalysisPipeline(args.output_path)
    pipeline.run(args.tickers)


if __name__ == "__main__":
    # Parse arguments
    arg = parser.parse_args([] if "__file__" not in globals() else None)
    main(arg)
