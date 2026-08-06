import shap
import pandas as pd
import numpy as np

class UnderwritingExplainer:
    def __init__(self, model, X_train):
        self.model = model
        # Using an abstract Explainer to safely support RandomForest, XGBoost, or LogisticRegression
        try:
            self.explainer = shap.TreeExplainer(model)
        except Exception:
            # Fallback to Kernel/Linear explainer if background sample data is required
            self.explainer = shap.Explainer(model.predict, shap.sample(X_train, min(len(X_train), 50)))
        
    def generate_force_plot_data(self, single_row_df: pd.DataFrame) -> dict:
        """Calculates exact feature importance weights for a single applicant's decision."""
        # Calculate shap expectations
        shap_values = self.explainer(single_row_df)
        
        # Extract values array cleanly depending on multi-class output shapes
        if len(shap_values.values.shape) == 3:  # Multi-class or explicit [samples, features, classes] shape
            raw_weights = shap_values.values[0, :, 1]
        elif len(shap_values.values.shape) == 2:  # Explicit [samples, features] binary shape
            raw_weights = shap_values.values[0]
        else:
            raw_weights = np.squeeze(shap_values.values)
            
        feature_importance = dict(zip(single_row_df.columns, map(float, raw_weights)))
        return feature_importance
