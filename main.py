import argparse
from data.connector.price import YahooPriceConnector
from data.connector.fundamental import YahooFundamentalsConnector
from analytics.price_analytics import PriceAnalytics

parser = argparse.ArgumentParser()

parser.add_argument("--tickers", nargs="+", type=str, help="list of tickers to be analyzed")

def main(args: argparse.Namespace):
    price_connector = YahooPriceConnector()
    fundamental_connector = YahooFundamentalsConnector()
    for ticker in args.tickers:
        print(ticker)
        prices = price_connector.fetch(ticker)
        fundamentals = fundamental_connector.fetch(ticker)
        analytics = PriceAnalytics(prices)
        print(analytics.summary())


if __name__ == "__main__":
    # Parse arguments
    arg = parser.parse_args([] if "__file__" not in globals() else None)
    main(arg)