import pandas as pd

class ComplianceFilter:
    def __init__(self):
        # RBI Fair Practices Code: Non-permissible demographic columns that cannot influence scoring
        self.prohibited_attributes = ['religion', 'caste', 'gender', 'race', 'political_affiliation']

    def audit_and_clean(self, df: pd.DataFrame):
        """Identifies and drops prohibited socio-demographic features before model exposure."""
        cleaned_df = df.copy()
        dropped = []
        
        for col in self.prohibited_attributes:
            if col in cleaned_df.columns:
                cleaned_df = cleaned_df.drop(columns=[col])
                dropped.append(col)
                
        return cleaned_df, dropped
