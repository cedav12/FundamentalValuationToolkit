import argparse
from data.pipeline import AnalysisPipeline

parser = argparse.ArgumentParser()
# General settings
parser.add_argument("--tickers", nargs="+", type=str, required=True, help="list of tickers to be analyzed")
parser.add_argument("--output_path", default="output_reports", type=str,
                    help="Specify path, where output will be saved. If None, no output will be saved")
parser.add_argument( "--show_plt", action="store_true",
                     help="If set, display plots interactively. Otherwise, just save to output_path.")
# Overrides
parser.add_argument("--growth", type=float, help="Override revenue growth")
parser.add_argument("--margin", type=float, help="Override target operating margin")
parser.add_argument("--wacc", type=float, help="Override WACC")
parser.add_argument("--terminal_growth", type=float, help="Override terminal growth rate")

def main(args: argparse.Namespace):
    overrides = {
        "revenue_growth_5y": args.growth,
        "operating_margin_target": args.margin,
        "wacc": args.wacc,
        "terminal_growth": args.terminal_growth        
    }
    overrides = {k: v for k, v in overrides.items() if v is not None}
# Initialize and execute pipeline
    pipeline = AnalysisPipeline(args.output_path, args.show_plt, overrides=overrides)
    pipeline.run(args.tickers)


if __name__ == "__main__":
    # Parse arguments and run
    arg = parser.parse_args([] if "__file__" not in globals() else None)
    main(arg)

