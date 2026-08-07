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
        
        # Enforce column structural defaults
        if 'product_type' not in processed.columns:
            processed['product_type'] = 'personal_loan'
        if 'collateral_val' not in processed.columns:
            processed['collateral_val'] = 0.0
        if 'dpd' not in processed.columns:
            processed['dpd'] = 0  # Default to performing if DPD column is absent
            
        # Standardise data format layouts
        processed[loan_amount_col] = pd.to_numeric(processed[loan_amount_col], errors='coerce').fillna(0.0)
        processed['collateral_val'] = pd.to_numeric(processed['collateral_val'], errors='coerce').fillna(0.0)
        processed['dpd'] = pd.to_numeric(processed['dpd'], errors='coerce').fillna(0).astype(int)
        processed['product_type'] = processed['product_type'].astype(str).str.strip().str.lower()
        
        # Maintain a dummy PD vector just to protect down-stream ReportLab hook calls
        processed['Probability_of_Default_PD'] = np.where(processed['dpd'] > 90, 0.45, 0.02)
        
        ead_arr, secured_arr, unsecured_arr, provision_arr, rwa_arr, grade_arr = [], [], [], [], [], []
        
        for idx, row in processed.iterrows():
            p_type = row['product_type']
            cfg = self.product_configs.get(p_type, {"ccf": 1.00, "risk_weight": 1.25})
            
            # Exposure At Default
            ead = row[loan_amount_col] * cfg['ccf']
            days_overdue = row['dpd']
            
            # =====================================================================
            # RBI IRACP DPD-BASED ASSET CLASSIFICATION MATRIX
            # =====================================================================
            if days_overdue == 0:
                grade = "Standard (Performing)"
            elif 1 <= days_overdue <= 30:
                grade = "Standard (SMA-0)"
            elif 31 <= days_overdue <= 60:
                grade = "Standard (SMA-1)"
            elif 61 <= days_overdue <= 90:
                grade = "Standard (SMA-2)"
            elif 91 <= days_overdue <= 180:
                grade = "Sub-Standard Asset"
            elif 181 <= days_overdue <= 365:
                grade = "Doubtful (Up to 1 Year)"
            elif 366 <= days_overdue <= 1095:
                grade = "Doubtful (1 to 3 Years)"
            else:
                grade = "Loss Asset"
            
            # Statutory override checks for Gold Loan LTV limits
            if p_type == "gold_loan" and "ltv_ratio" in row.index:
                try:
                    if float(row["ltv_ratio"]) > 0.75:
                        grade = "CRITICAL BREACH: LTV > 75%"
                except (ValueError, TypeError):
                    pass

            # Collateral Value Asset Splitting
            secured_amt = min(ead, float(row['collateral_val']))
            unsecured_amt = max(0.0, ead - secured_amt)
            
            # =====================================================================
            # FIXED MATHEMATICAL PROVISION MULTIPLIERS (RBI ALIGNED)
            # =====================================================================
            if "Standard" in grade:
                prov_sec = secured_amt * 0.0040    
                prov_unsec = unsecured_amt * 0.0040 # 0.40% flat standard provisioning
            elif grade == "Sub-Standard Asset":
                prov_sec = secured_amt * 0.10      
                prov_unsec = unsecured_amt * 0.20  # 20% on unsecured sub-standard lines
            else:
                # Enforce absolute 100% write-down provisioning on unsecured doubtful/loss components
                prov_sec = secured_amt * (0.25 if grade == "Doubtful (Up to 1 Year)" else 0.40 if grade == "Doubtful (1 to 3 Years)" else 1.00)
                prov_unsec = unsecured_amt * 1.00  
                
            total_provision = prov_sec + prov_unsec
            rwa = ead * cfg['risk_weight']
            
            ead_arr.append(ead)
            secured_arr.append(secured_amt)
            unsecured_arr.append(unsecured_amt)
            provision_arr.append(total_provision)
            rwa_arr.append(rwa)
            grade_arr.append(grade)
            
        processed['EAD'] = ead_arr
        processed['Secured_Exposure'] = secured_arr
        processed['Unsecured_Exposure'] = unsecured_arr
        processed['RBI_Mandated_Provision'] = provision_arr
        processed['RWA'] = rwa_arr
        processed['Risk_Classification'] = grade_arr
        
        return processed
