import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass

# Class for holding scenario assumptions
class DCFAssumptions:
    name: str
    gr_next5y: float
    operating_margin_target: float
    tax_rate: float
    roic_target: float
    wacc: float
    terminal_gr: float
    shares_outst: float
    net_debt: float

# Performs DCF valuation
class DCFModel:

    # Projects FCF for upcoming 5y - calculates terminal value, returns share price and detailed projections
    def fair_val_calc(self, current_rev: float, assumptions: DCFAssumptions) -> dict:
        years = range(1, 6)  # forcast dataframe setup
        projections = pd.DataFrame(index=years, columns=["Revenue","EBIT","NOPAT","Reinvestment","FCF","PV_FCF"])
        prev_rev = current_rev

        for year in years:
            rev = prev_rev*(1 + assumptions.gr_next5y) # revenue growth
            ebit = rev * assumptions.operating_margin_target
            nopat = ebit * (1 - assumptions.tax_rate)

            # Value driver: Reinvestment rate = g / ROIC
            if assumptions.roic_target > 0: 
                reinvest_rate = assumptions.gr_next5y/assumptions.roic_target
            else:
                reinvest_rate = 0

            investment = nopat*reinvest_rate
            
            fcf = nopat - investment

            discount_factor = (1 + assumptions.wacc) ** year
            pv_fcf = fcf/discount_factor

            projections.loc[year] = [rev, ebit, nopat, investment, fcf, pv_fcf]
            prev_rev = rev

        # Terminal Value formula
        last_nopat = projections.loc[5, "NOPAT"]
        terminal_nopat = last_nopat*(1 + assumptions.terminal_gr)
        if assumptions.roic_target > 0:
            tv_reinvest_rate = assumptions.terminal_gr/assumptions.roic_target
        else:
            tv_reinvest_rate = 0
        terminal_fcf = terminal_nopat*(1 - tv_reinvest_rate)
        terminal_val = terminal_fcf / max(assumptions.wacc - assumptions.terminal_gr, 0.001)
        pv_terminal_val = terminal_val/ ((1 + assumptions.wacc)**5)

        # Total Enterprise Value
        sum_pv_fcf = projections["PV_FCF"].sum()
        enterprise_val = sum_pv_fcf + pv_terminal_val

        # Equity Value
        equity_val = enterprise_val - assumptions.net_debt

        #Price per share
        share_price = equity_val/ (assumptions.shares_outst if assumptions.shares_outst > 0 else 1)

        return {
            "scenario": assumptions.name,
            "share_price": share_price,
            "enterprise_value": enterprise_val,
            "equity_value": equity_val,
            "projections": projections,
            "terminal_value": terminal_val
        }