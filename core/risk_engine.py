import pandas as pd
import numpy as np

class ComplianceRiskEngine:
    def __init__(self, model):
        self.model = model
        
        # RBI Standard Provisioning Parameters per portfolio asset profile
        self.product_configs = {
            "home_loan":     {"lgd": 0.20, "ccf": 1.00}, 
            "gold_loan":     {"lgd": 0.12, "ccf": 1.00}, 
            "bike_loan":     {"lgd": 0.45, "ccf": 1.00}, 
            "personal_loan": {"lgd": 0.65, "ccf": 1.00}, 
            "credit_card":   {"lgd": 0.85, "ccf": 0.50}  
        }

    def calculate_ecl(self, df: pd.DataFrame, loan_amount_col: str) -> pd.DataFrame:
        processed = df.copy()
        
        if 'product_type' not in processed.columns:
            processed['product_type'] = 'personal_loan'
            
        # Simulate / Predict individual transaction risk scores
        np.random.seed(42)
        processed['Probability_of_Default_PD'] = np.random.uniform(0.00, 0.50, size=len(processed))
        
        def run_regulatory_math(row):
            p_type = row['product_type'] if row['product_type'] in self.product_configs else 'personal_loan'
            cfg = self.product_configs[p_type]
            
            ead = row[loan_amount_col] * cfg['ccf']
            ecl = row['Probability_of_Default_PD'] * cfg['lgd'] * ead
            
            # =====================================================================
            # RBI IRACP SYSTEM: Map default probabilities into real banking tags
            # =====================================================================
            pd_score = row['Probability_of_Default_PD']
            
            if pd_score <= 0.05:
                grade = "Standard (Performing)"
            elif 0.05 < pd_score <= 0.12:
                grade = "Standard (SMA-0)"
            elif 0.12 < pd_score <= 0.20:
                grade = "Standard (SMA-1)"
            elif 0.20 < pd_score <= 0.25:
                grade = "Standard (SMA-2)"
            elif 0.25 < pd_score <= 0.38:
                grade = "Sub-Standard Asset (NPA)"
            elif 0.38 < pd_score <= 0.46:
                grade = "Doubtful Asset (NPA)"
            else:
                grade = "Loss Asset"
                
            # Additional structural check: Gold loan LTV limit breaches 
            if p_type == "gold_loan" and "ltv_ratio" in row.index and row["ltv_ratio"] > 0.75:
                grade = "CRITICAL BREACH: LTV > 75% (Statutory Violation)"
                
            return pd.Series([ead, ecl, grade])

        processed[['Exposure_at_Default_EAD', 'Expected_Credit_Loss_ECL', 'Risk_Classification']] = processed.apply(
            run_regulatory_math, axis=1
        )
        return processed
