ingimport pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass

# Holds key inputs
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

class DCFModel:

    # Projects FCF for upcoming 5y - calculates terminal value, returns share price and detailed projections
    @staticmethod
    def run_dcf(current_rev: float, assumptions: DCFAssumptions) -> dict:
        years = range(1, 6)  # forcast dataframe setup
        projections = pd.DataFrame(index=years, columns=["Revenue","EBIT","NOPAT","Reinvestment","FCF","PV_FCF"])
        prev_rev = current_rev

        for year in years:
            # Operating performance
            rev = prev_rev*(1 + assumptions.gr_next5y)
            ebit = rev * assumptions.operating_margin_target
            nopat = ebit * (1 - assumptions.tax_rate)

            # Value driver: Reinvestment rate = g / ROIC
            if assumptions.roic_target > 0: 
                reinvest_rate = assumptions.gr_next5y/assumptions.roic_target
            else:
                reinvest_rate = 0

            investment = nopat*reinvest_rate
            
            fcf = nopat - investment

            # Discount to present value
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

        # Equity value per share
        sum_pv_fcf = projections["PV_FCF"].sum()
        enterprise_val = sum_pv_fcf + pv_terminal_val
        equity_val = enterprise_val - assumptions.net_debt
        share_price = equity_val/ (assumptions.shares_outst if assumptions.shares_outst > 0 else 1)

        return {
            "scenario": assumptions.name,
            "share_price": share_price,
            "enterprise_value": enterprise_val,
            "equity_value": equity_val,
            "projections": projections,
            "terminal_value": terminal_val
        }

    # Calculates share price for a matrix of WACC x terminal growth rates (9 total), and returns a dataframe for pricing.
    @staticmethod
    def run_sensitivity_analysis(current_rev: float, base_assumptions: DCFAssumptions) -> pd.DataFrame:
        wacc_range = [base_assumptions.wacc - 0.01, base_assumptions.wacc, base_assumptions.wacc + 0.01]
        growth_range= [base_assumptions.terminal_gr - 0.01, base_assumptions.terminal_gr, base_assumptions.terminal_gr + 0.01]
        results = {}

        # Clones assumptions to avoid changing the original
        temp_assumptions = DCFAssumptions(
            name = base_assumptions.name,
            gr_next5y = base_assumptions.gr_next5y,
            operating_margin_target=base_assumptions.operating_margin_target,
            tax_rate = base_assumptions.tax_rate,
            roic_target= base_assumptions.roic_target,
            wacc= base_assumptions.wacc,
            terminal_gr = base_assumptions.terminal_gr,
            shares_outst = base_assumptions.shares_outst,
            net_debt = base_assumptions.net_debt
        )

        for g in growth_range:
            row_results = []
            for w in wacc_range:
                temp_assumptions.wacc = w
                temp_assumptions.terminal_gr = g
                res = DCFModel.run_dcf(current_rev,temp_assumptions)
                row_results.append(round(res["share_price"], 2))
            results[f"Terminal Growth {g:.1%}"] = row_results

        df= pd.DataFrame(results, index=[f"WACC {w:.1%}" for w in wacc_range])
        return df
            
        





