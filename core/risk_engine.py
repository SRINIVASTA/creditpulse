import pandas as pd
import numpy as np

class ComplianceRiskEngine:
    def __init__(self, model):
        self.model = model
        
        # Statutory RBI Portfolio Weights & CCF rules per product line
        self.product_configs = {
            "home_loan":     {"ccf": 1.00, "risk_weight": 0.50},  # Secured by Property
            "gold_loan":     {"ccf": 1.00, "risk_weight": 0.00},  # Secured by Liquid Gold
            "bike_loan":     {"ccf": 1.00, "risk_weight": 1.00},  # SECURED BY BIKE HYPOTHECATION
            "personal_loan": {"ccf": 1.00, "risk_weight": 1.25},  # Completely Unsecured Term
            "credit_card":   {"ccf": 0.50, "risk_weight": 1.25}   # Completely Unsecured Revolving
        }

    def calculate_ecl(self, df: pd.DataFrame, loan_amount_col: str) -> pd.DataFrame:
        processed = df.copy()
        
        # Ensure standard banking headers are present
        if 'product_type' not in processed.columns:
            processed['product_type'] = 'credit_card'
        if 'limit_bal' not in processed.columns:
            processed['limit_bal'] = processed['LIMIT_BAL'] if 'LIMIT_BAL' in processed.columns else 100000.0
        if 'collateral_val' not in processed.columns:
            processed['collateral_val'] = 0.0
            
        # Dynamically map PAY_0 status indexes cleanly to standard Indian Days Past Due (DPD)
        if 'dpd' not in processed.columns:
            status_col = 'PAY_0' if 'PAY_0' in processed.columns else 'pay_0' if 'pay_0' in processed.columns else None
            if status_col:
                processed['dpd'] = processed[status_col].apply(lambda x: max(0, int(x) * 30))
            else:
                processed['dpd'] = 0

        # Enforce exact floating point types
        processed[loan_amount_col] = pd.to_numeric(processed[loan_amount_col], errors='coerce').fillna(0.0)
        processed['limit_bal'] = pd.to_numeric(processed['limit_bal'], errors='coerce').fillna(0.0)
        processed['collateral_val'] = pd.to_numeric(processed['collateral_val'], errors='coerce').fillna(0.0)
        processed['dpd'] = pd.to_numeric(processed['dpd'], errors='coerce').fillna(0).astype(int)
        processed['product_type'] = processed['product_type'].astype(str).str.strip().str.lower()

        ead_arr, secured_arr, unsecured_arr, provision_arr, rwa_arr, grade_arr = [], [], [], [], [], []
        
        for idx, row in processed.iterrows():
            p_type = row['product_type']
            cfg = self.product_configs.get(p_type, {"ccf": 1.00, "risk_weight": 1.25})
            
            # Exposure At Default Calculation
            balance = float(row[loan_amount_col])
            limit = float(row['limit_bal'])
            ead = balance + (max(0.0, limit - balance) * cfg['ccf'])
            
            # =====================================================================
            # RBI SECURED PROPERTY RULES: Force collateral values based on product type
            # =====================================================================
            if p_type in ['credit_card', 'personal_loan']:
                # Clean Unsecured: No collateral allowed
                collateral_backing = 0.0
            elif p_type == 'bike_loan':
                # SECURED: The bike itself acts as collateral. We evaluate its depreciated value.
                # If collateral value is missing or 0 in the CSV, we fall back to a conservative 80% of loan value
                collateral_backing = float(row['collateral_val']) if float(row['collateral_val']) > 0 else ead * 0.80
            else:
                # Home and Gold Loans read directly from verified asset valuations
                collateral_backing = float(row['collateral_val'])
            
            # RBI IRACP DPD Time Bucket Classification Waterfall
            days_overdue = int(row['dpd'])
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

            # Dynamic Collateral Asset Splitting
            secured_amt = min(ead, collateral_backing)
            unsecured_amt = max(0.0, ead - secured_amt)
            
            # Enforce Mandated Provision Percentages (RBI IRACP Aligned)
            if "Standard" in grade:
                prov_sec = secured_amt * 0.0040    
                prov_unsec = unsecured_amt * 0.0040
            elif grade == "Sub-Standard Asset":
                prov_sec = secured_amt * 0.10      # 10% provision on secured portion (like Bike value)
                prov_unsec = unsecured_amt * 0.20  # 20% provision on any unsecured gap
            else:
                prov_sec = secured_amt * (0.25 if grade == "Doubtful (Up to 1 Year)" else 0.40 if grade == "Doubtful (1 to 3 Years)" else 1.00)
                prov_unsec = unsecured_amt * 1.00  # 100% write-down required for unsecured portions
                
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
