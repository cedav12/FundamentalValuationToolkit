import argparse
from data.connector.price import YahooPriceConnector
from data.connector.fundamental import YahooFundamentalsConnector
from analytics.ec_metric_processor import FundamentalProcessor
from data.models.fundamental_data import FundamentalData
from analytics.price_analytics import PriceAnalytics

parser = argparse.ArgumentParser()

parser.add_argument("--tickers", nargs="+", type=str, help="list of tickers to be analyzed")

def main(args: argparse.Namespace):
    price_connector = YahooPriceConnector()
    fundamental_connector = YahooFundamentalsConnector()
    print("ANALYSIS STARTED:")
    for ticker in args.tickers:
        print("\n" + 10 * "="+ "\n" + f"ANALYZING {ticker}...\n")
        print("Fundamental Analysis:")
        fundementals: FundamentalData = fundamental_connector.fetch(ticker)
        processor = FundamentalProcessor(fundementals)
        metrics = processor.get_metrics()
        if metrics is not None:
            print(f"\n--- Key Metrics for {ticker} (Last 5 years) ---")
            print(metrics[["Revenue", "NOPAT", "ROIC", "FCF"]].tail(5))

        print("\nFinancial Analysis:")
        prices = price_connector.fetch(ticker)
        price_analysis = PriceAnalytics(prices)
        print(price_analysis.summary())


if __name__ == "__main__":
    # Parse arguments
    arg = parser.parse_args([] if "__file__" not in globals() else None)
    main(arg)