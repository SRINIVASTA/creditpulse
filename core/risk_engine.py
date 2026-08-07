import pandas as pd
import numpy as np

class ComplianceRiskEngine:
    def __init__(self, model):
        self.model = model
        
        # Product configuration for Exposure at Default (EAD)
        self.product_configs = {
            "home_loan":     {"ccf": 1.00, "risk_weight": 0.50},  # 50% Capital Weight for Residential Mortgage
            "gold_loan":     {"ccf": 1.00, "risk_weight": 0.00},  # Liquid Gold collateral reduces capital charge
            "bike_loan":     {"ccf": 1.00, "risk_weight": 1.00},  # Standard consumer auto assets 
            "personal_loan": {"ccf": 1.00, "risk_weight": 1.25},  # 125% Elevated Risk Weight via recent RBI tightening
            "credit_card":   {"ccf": 0.50, "risk_weight": 1.25}   # High risk revolving unsecured credit lines
        }

    def calculate_ecl(self, df: pd.DataFrame, loan_amount_col: str) -> pd.DataFrame:
        processed = df.copy()
        
        if 'product_type' not in processed.columns:
            processed['product_type'] = 'personal_loan'
            
        np.random.seed(42)
        processed['Probability_of_Default_PD'] = np.random.uniform(0.00, 0.50, size=len(processed))
        
        def compute_rbi_provisions(row):
            p_type = row['product_type'] if row['product_type'] in self.product_configs else 'personal_loan'
            cfg = self.product_configs[p_type]
            
            # 1. Calculate Exposure at Default (EAD)
            ead = row[loan_amount_col] * cfg['ccf']
            
            # 2. Assign Risk Classification Bucket
            pd_score = row['Probability_of_Default_PD']
            if pd_score <= 0.05:
                grade = "Standard (Performing)"
            elif 0.05 < pd_score <= 0.12:
                grade = "Standard (SMA-0)"
            elif 0.12 < pd_score <= 0.20:
                grade = "Standard (SMA-1)"
            elif 0.20 < pd_score <= 0.25:
                grade = "Standard (SMA-2)"
            elif 0.25 < pd_score <= 0.35:
                grade = "Sub-Standard Asset"
            elif 0.35 < pd_score <= 0.42:
                grade = "Doubtful (Up to 1 Year)"
            elif 0.42 < pd_score <= 0.47:
                grade = "Doubtful (1 to 3 Years)"
            else:
                grade = "Loss Asset"
            
            if p_type == "gold_loan" and "ltv_ratio" in row.index and row["ltv_ratio"] > 0.75:
                grade = "CRITICAL BREACH: LTV > 75%"

            # 3. Dynamic Asset Bifurcation (Secured vs Unsecured Breakdown)
            collateral = row['collateral_val'] if 'collateral_val' in row.index else 0
            secured_amt = min(ead, collateral)
            unsecured_amt = max(0, ead - secured_amt)
            
            # 4. Apply RBI Statutory Provision Percentages
            if "Standard" in grade:
                prov_sec = secured_amt * 0.0040    # 0.40% Standard Asset Provisioning
                prov_unsec = unsecured_amt * 0.0040
            elif grade == "Sub-Standard Asset":
                prov_sec = secured_amt * 0.10      # 10% on Secured Portion
                prov_unsec = unsecured_amt * 0.20  # 20% on Unsecured Portion
            elif grade == "Doubtful (Up to 1 Year)":
                prov_sec = secured_amt * 0.25      # 25% Secured
                prov_unsec = unsecured_amt * 1.00  # 100% Unsecured
            elif grade == "Doubtful (1 to 3 Years)":
                prov_sec = secured_amt * 0.40      # 40% Secured
                prov_unsec = unsecured_amt * 1.00  # 100% Unsecured
            else: # Loss Assets & Statutory Breaches
                prov_sec = secured_amt * 1.00      # 100% Fully Impaired
                prov_unsec = unsecured_amt * 1.00
                
            total_provision = prov_sec + prov_unsec
            
            # 5. Capital Requirements Math: Risk Weighted Assets (RWA)
            rwa = ead * cfg['risk_weight']
            
            return pd.Series([ead, secured_amt, unsecured_amt, total_provision, rwa, grade])

        (processed['EAD'], processed['Secured_Exposure'], processed['Unsecured_Exposure'], 
         processed['RBI_Mandated_Provision'], processed['RWA'], processed['Risk_Classification']) = zip(*processed.apply(compute_rbi_provisions, axis=1))
         
        return processed
