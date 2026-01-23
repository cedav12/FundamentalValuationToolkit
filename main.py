import argparse
from data.connector.price import YahooPriceConnector
from data.connector.fundamental import YahooFundamentalsConnector
from analytics.ec_metric_processor import FundamentalProcessor
from data.models.fundamental_data import FundamentalData
from analytics.price_analytics import PriceAnalytics
from analytics.valuation import DCFModel, DCFAssumptions

parser = argparse.ArgumentParser()

parser.add_argument("--tickers", nargs="+", type=str, help="list of tickers to be analyzed")

def main(args: argparse.Namespace):
    price_connector = YahooPriceConnector()
    fundamental_connector = YahooFundamentalsConnector()
    dcf = DCFModel()
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
            latest = processor.get_latest_data()
            base_assumptions = DCFAssumptions(
                name= "Base Case",
                gr_next5y=0.05,
                operating_margin_target=0.20,
                tax_rate=0.21,
                roic_target=latest["roic"],
                wacc=0.08,
                terminal_gr=0.03,
                shares_outst=latest["shares"],
                net_debt=latest["net_debt"]
            )
        print("\nValuation Model (DCF)")
        try:
            result = dcf.run_dcf(latest["revenue"], base_assumptions)
            print(f"Scenario: {result['scenario']}")
            print(f"Estemated fair value per share: ${result['share_price']:.2f}")
            intr_val=result['share_price']
        except Exception as e:
            print(f"Valuation failed: {e}")
            intr_val = 0
            
        print("\nFinancial Analysis:")
        try:
            prices = price_connector.fetch(ticker)
            price_analysis = PriceAnalytics(prices)
            print(price_analysis.summary())
            curr_price = prices['Close'].iloc[-1]
            print(f"Current Market Price: ${curr_price:.2f}")

            if metrics is not None and intr_val > 0:
                upside = (intr_val - curr_price) / curr_price
                print(f"Implied Upside: {upside:.1%}")
            print("\nRisk Metrics:")
            print(summary)
        
        except Exception as e:
            print(f"Price analysis failed: {e}")

if __name__ == "__main__":
    # Parse arguments
    arg = parser.parse_args([] if "__file__" not in globals() else None)
    main(arg)
