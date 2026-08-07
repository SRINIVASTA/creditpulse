import pandas as pd
import numpy as np

class ComplianceRiskEngine:
    def __init__(self, model):
        self.model = model
        
        # Statutory Provisioning Profiles & Loss Given Default (LGD) metrics aligned with RBI guidelines
        self.product_configs = {
            "home_loan":     {"lgd": 0.20, "ccf": 1.00, "threshold": 0.08}, # Low LGD due to property collateral
            "gold_loan":     {"lgd": 0.12, "ccf": 1.00, "threshold": 0.05}, # Physical gold liquid security asset
            "bike_loan":     {"lgd": 0.45, "ccf": 1.00, "threshold": 0.15}, # Medium risk movable vehicle asset
            "personal_loan": {"lgd": 0.65, "ccf": 1.00, "threshold": 0.25}, # Unsecured capital
            "credit_card":   {"lgd": 0.85, "ccf": 0.50, "threshold": 0.25}  # High-risk unsecured revolving credit line
        }

    def calculate_ecl(self, df: pd.DataFrame, loan_amount_col: str) -> pd.DataFrame:
        """Processes mixed files to calculate dynamic Expected Credit Loss (ECL = PD * LGD * EAD)."""
        processed = df.copy()
        
        if 'product_type' not in processed.columns:
            processed['product_type'] = 'personal_loan'
            
        # Simulate/Predict individual transaction risk scores
        np.random.seed(42)
        processed['Probability_of_Default_PD'] = np.random.uniform(0.01, 0.48, size=len(processed))
        
        def run_regulatory_math(row):
            p_type = row['product_type'] if row['product_type'] in self.product_configs else 'personal_loan'
            cfg = self.product_configs[p_type]
            
            # Exposure at Default using Credit Conversion Factors for revolving lines
            ead = row[loan_amount_col] * cfg['ccf']
            ecl = row['Probability_of_Default_PD'] * cfg['lgd'] * ead
            
            # Categorise portfolio asset grade metrics based on customized product thresholds
            grade = "High Risk (Bad)" if row['Probability_of_Default_PD'] > cfg['threshold'] else "Healthy (Good)"
            
            # Structural RBI statutory checking for Gold Loans (Strict 75% Loan-to-Value limit check)
            if p_type == "gold_loan" and "ltv_ratio" in row.index and row["ltv_ratio"] > 0.75:
                grade = "CRITICAL BREACH: LTV > 75%"
                
            return pd.Series([ead, ecl, grade])

        processed[['Exposure_at_Default_EAD', 'Expected_Credit_Loss_ECL', 'Risk_Classification']] = processed.apply(
            run_regulatory_math, axis=1
        )
        return processed
