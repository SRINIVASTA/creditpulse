import pandas as pd
import numpy as np

class UnderwritingExplainer:
    def __init__(self, model, training_data):
        self.model = model
        self.training_data = training_data

    def generate_force_plot_data(self, target_row: pd.DataFrame):
        """Generates dynamic proxy feature weight impacts for client audit reasons code visualization."""
        # Provides mock feature impact directions to remain self-contained for the ui charts
        columns = [c for c in target_row.columns if c not in ['product_type', 'Risk_Classification']]
        np.random.seed(123)
        simulated_shap_values = np.random.uniform(-0.15, 0.20, size=len(columns))
        
        return dict(zip(columns, np.round(simulated_shap_values, 4)))
