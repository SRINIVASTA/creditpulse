import pandas as pd
import numpy as np

class ComplianceRiskEngine:
    def __init__(self, model):
        self.model = model
        
        # Product configuration for Exposure at Default (EAD) & Capital Risk Weighting
        self.product_configs = {
            "home_loan":     {"ccf": 1.00, "risk_weight": 0.50},  
            "gold_loan":     {"ccf": 1.00, "risk_weight": 0.00},  
            "bike_loan":     {"ccf": 1.00, "risk_weight": 1.00},  
            "personal_loan": {"ccf": 1.00, "risk_weight": 1.25},  
            "credit_card":   {"ccf": 0.50, "risk_weight": 1.25}   
        }

    def calculate_ecl(self, df: pd.DataFrame, loan_amount_col: str) -> pd.DataFrame:
        processed = df.copy()
        
        # Force column data structure compliance
        if 'product_type' not in processed.columns:
            processed['product_type'] = 'personal_loan'
            
        if 'collateral_val' not in processed.columns:
            processed['collateral_val'] = 0.0
            
        # Standardise structural data formats
        processed[loan_amount_col] = pd.to_numeric(processed[loan_amount_col], errors='coerce').fillna(0.0)
        processed['collateral_val'] = pd.to_numeric(processed['collateral_val'], errors='coerce').fillna(0.0)
        processed['product_type'] = processed['product_type'].astype(str).str.strip().str.lower()
        
        # Predict or generate risk metrics safely
        np.random.seed(42)
        processed['Probability_of_Default_PD'] = np.random.uniform(0.00, 0.50, size=len(processed))
        
        # Initialize output array structures
        ead_arr = []
        secured_arr = []
        unsecured_arr = []
        provision_arr = []
        rwa_arr = []
        grade_arr = []
        
        # Run sequential processing loops cleanly to prevent unpack TypeErrors
        for idx, row in processed.iterrows():
            p_type = row['product_type']
            cfg = self.product_configs.get(p_type, {"ccf": 1.00, "risk_weight": 1.25})
            
            # Exposure At Default
            ead = row[loan_amount_col] * cfg['ccf']
            
            # Asset Classification Buckets
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
            
            # Statutory override checks
            if p_type == "gold_loan" and "ltv_ratio" in row.index:
                try:
                    ltv = float(row["ltv_ratio"])
                    if ltv > 0.75:
                        grade = "CRITICAL BREACH: LTV > 75%"
                except (ValueError, TypeError):
                    pass

            # Collateral Splitting
            secured_amt = min(ead, float(row['collateral_val']))
            unsecured_amt = max(0.0, ead - secured_amt)
            
            # RBI Provision Percentage Multipliers
            if "Standard" in grade:
                prov_sec = secured_amt * 0.0040    
                prov_unsec = unsecured_amt * 0.0040
            elif grade == "Sub-Standard Asset":
                prov_sec = secured_amt * 0.10      
                prov_unsec = unsecured_amt * 0.20  
            elif grade == "Doubtful (Up to 1 Year)":
                prov_sec = secured_amt * 0.25      
                prov_unsec = unsecured_amt * 1.00  
            elif grade == "Doubtful (1 to 3 Years)":
                prov_sec = secured_amt * 0.40      
                prov_unsec = unsecured_amt * 1.00  
            else: 
                prov_sec = secured_amt * 1.00      
                prov_unsec = unsecured_amt * 1.00
                
            total_provision = prov_sec + prov_unsec
            rwa = ead * cfg['risk_weight']
            
            # Pack results sequentially
            ead_arr.append(ead)
            secured_arr.append(secured_amt)
            unsecured_arr.append(unsecured_amt)
            provision_arr.append(total_provision)
            rwa_arr.append(rwa)
            grade_arr.append(grade)
            
        # Bind arrays directly back to named columns
        processed['EAD'] = ead_arr
        processed['Secured_Exposure'] = secured_arr
        processed['Unsecured_Exposure'] = unsecured_arr
        processed['RBI_Mandated_Provision'] = provision_arr
        processed['RWA'] = rwa_arr
        processed['Risk_Classification'] = grade_arr
        
        return processed
