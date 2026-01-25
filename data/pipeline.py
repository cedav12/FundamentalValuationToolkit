import os
import datetime

import pandas as pd

from data.logger import Logger
from data.connector.price import YahooPriceConnector
from data.connector.fundamental import YahooFundamentalsConnector
from analytics.ec_metric_processor import FundamentalProcessor
from analytics.price_analytics import PriceAnalytics
from analytics.valuation import DCFModel, DCFAssumptions
from data.models.fundamental_data import FundamentalData
from data.plotter import Plotter


class AnalysisPipeline:
    """
    Orchestrates full equity analysis in small, testable steps.
    """
    def __init__(self, output_path: str | None = None, show_plt: bool = False):
        self.show_plt = show_plt
        self.output_path = output_path

        # Shared services
        self.price_connector = YahooPriceConnector()
        self.fundamental_connector = YahooFundamentalsConnector()
        self.dcf_model = DCFModel()

    # =====================================================
    # Public API
    # =====================================================
    def run(self, tickers: list[str]):
        print("ANALYSIS STARTED:")
        for ticker in tickers:
            self._analyze_ticker(ticker.upper())
        print("\nANALYSIS FINISHED.")
        if self.output_path is not None:
            print(f"Reports saved in: ./{self.output_path}/")

    # =====================================================
    # Per-ticker pipeline
    # =====================================================
    def _analyze_ticker(self, ticker: str):
        logger = self._create_logger(ticker)
        try:
            self._write_header(logger, ticker)
            prices = self._run_price_analysis(logger, ticker)
            self._run_fundamental_analysis(prices, logger, ticker)
        except Exception as e:
            logger.log(f"Unexpected pipeline failure: {e}")
        finally:
            logger.close()

    # =====================================================
    # Setup
    # =====================================================
    def _create_logger(self, ticker: str) -> Logger:
        path = os.path.join(self.output_path, ticker, f"{ticker}_report.txt") if self.output_path else None
        return Logger(path)

    @staticmethod
    def _write_header(logger: Logger, ticker: str):

        logger.section(
            f"Ticker: {ticker}\nRun Time: {datetime.datetime.now()}"
        )

    # =====================================================
    # Price Analysis
    # =====================================================
    def _run_price_analysis(self, logger: Logger, ticker: str) -> pd.DataFrame | None:
        logger.subsection("Risk and Performance Metrics")
        try:
            prices = self.price_connector.fetch(ticker)
            analysis = PriceAnalytics(prices)
            summary = analysis.summary()
            logger.log(summary)
            # Price MA plot
            Plotter.plot_price_ma(prices, logger.log_dir, ticker, self.show_plt)
            return prices

        except Exception as e:

            logger.log(f"Price analysis failed {e}")
            return None

    # =====================================================
    # Fundamental Analysis
    # =====================================================
    def _run_fundamental_analysis(
        self,
        prices: pd.DataFrame,
        logger: Logger,
        ticker: str
    ) -> None:
        logger.subsection("\nFundamental Analysis:")
        fundementals: FundamentalData = self.fundamental_connector.fetch(ticker)
        processor = FundamentalProcessor(fundementals, logger)
        metrics = processor.get_metrics()
        if metrics is not None:
            logger.subsection(f"Key Metrics for {ticker} (Last 5 years)")
            logger.log(metrics[["Revenue", "NOPAT", "ROIC", "FCF"]].tail(5))
            latest = processor.get_latest_data()
            base_assumptions = self._build_dcf_assumptions(latest)
            logger.subsection("\nValuation Model (DCF)")
            try:
                result = self.dcf_model.run_dcf(latest["rev"], base_assumptions)
                logger.log(f"Scenario: {result['scenario']}")
                logger.log(f"Estimated fair value per share: ${result['share_price']:.2f}")
                intr_val = result['share_price']
                curr_price = prices['Close'].iloc[-1]
                logger.log(f"Current Market Price: ${curr_price:.2f}")
                upside = (intr_val - curr_price) / curr_price
                logger.log(f"Implied Upside: {upside:.1%}")
                # Revenue / FCF plot
                Plotter.plot_revenue_fcf(metrics, logger.log_dir, ticker, self.show_plt)
                # ROIC vs WACC
                Plotter.plot_roic_vs_wacc(metrics, base_assumptions.wacc, logger.log_dir, ticker, self.show_plt)
                # Price vs DCF (after DCF calculated)
                Plotter.plot_price_vs_dcf(prices, intr_val, logger.log_dir, ticker, self.show_plt)
            except Exception as e:
                logger.log(f"DCF analysis failed: {e}")

    def _build_dcf_assumptions(self, latest: dict) -> DCFAssumptions:

        return DCFAssumptions(
            name="Base Case",
            gr_next5y=0.05,
            operating_margin_target=0.20,
            tax_rate=0.21,  # 21% - https://en.wikipedia.org/wiki/Corporate_tax_in_the_United_States
            roic_target=latest["roic"],
            wacc=0.08,
            terminal_gr=0.03,
            shares_outst=latest["shares"],
            net_debt=latest["net_debt"],
        )
