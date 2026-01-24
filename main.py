import os
import argparse


from data.logger import Logger
from data.connector.price import YahooPriceConnector
from data.connector.fundamental import YahooFundamentalsConnector
from analytics.ec_metric_processor import FundamentalProcessor
from data.models.fundamental_data import FundamentalData
from analytics.price_analytics import PriceAnalytics
from analytics.valuation import DCFModel, DCFAssumptions

parser = argparse.ArgumentParser()

parser.add_argument("--tickers", nargs="+", type=str, help="list of tickers to be analyzed")
parser.add_argument("--output_path", default="output_reports", type=str,
                    help="Specify path, where output will be saved. If None, no output will be saved")

def main(args: argparse.Namespace):
    price_connector = YahooPriceConnector()
    fundamental_connector = YahooFundamentalsConnector()
    dcf = DCFModel()
    print("ANALYSIS STARTED:")
    for ticker in args.tickers:
        logger = Logger(os.path.join(args.output_path, f"{ticker}.txt"))
        logger.log("\n" + 10 * "="+ "\n" + f"ANALYZING {ticker}...\n")
        logger.log("Risk and Performance Metrics:")
        prices = price_connector.fetch(ticker)
        price_analysis = PriceAnalytics(prices)
        summary = price_analysis.summary()
        logger.log(summary)

        logger.log("\nFundamental Analysis:")
        fundementals: FundamentalData = fundamental_connector.fetch(ticker)
        processor = FundamentalProcessor(fundementals, logger)
        metrics = processor.get_metrics()
        if metrics is not None:
            logger.log(f"\n--- Key Metrics for {ticker} (Last 5 years) ---")
            logger.log(metrics[["Revenue", "NOPAT", "ROIC", "FCF"]].tail(5))
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
            logger.log("\nValuation Model (DCF)")
            try:
                result = dcf.run_dcf(latest["rev"], base_assumptions)
                logger.log(f"Scenario: {result['scenario']}")
                logger.log(f"Estemated fair value per share: ${result['share_price']:.2f}")
                intr_val=result['share_price']
                curr_price = prices['Close'].iloc[-1]
                logger.log(f"Current Market Price: ${curr_price:.2f}")
                upside = (intr_val - curr_price) / curr_price
                logger.log(f"Implied Upside: {upside:.1%}")
            except Exception as e:
                logger.log(f"DCF analysis failed: {e}")

        logger.close()

    print("\nANALYSIS FINISHED.")
    if args.output_path is not None:
        print(f"Output reports are available at specified path ('/{args.output_path}/').")




if __name__ == "__main__":
    # Parse arguments
    arg = parser.parse_args([] if "__file__" not in globals() else None)
    main(arg)
