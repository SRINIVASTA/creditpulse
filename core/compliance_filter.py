import pandas as pd

class ComplianceFilter:
    def __init__(self):
        # RBI Fair Lending Directives restrict credit decisions based on demographic bias parameters
        self.protected_attributes = ['age', 'gender', 'religion', 'caste', 'marital_status']

    def audit_and_clean(self, df: pd.DataFrame):
        """Removes protected parameters while preserving core underwriting columns."""
        cleaned_df = df.copy()
        dropped_cols = []
        
        for col in self.protected_attributes:
            if col in cleaned_df.columns:
                cleaned_df = cleaned_df.drop(columns=[col])
                dropped_cols.append(col)
                
        return cleaned_df, dropped_cols
