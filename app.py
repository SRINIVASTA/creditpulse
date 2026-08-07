import os
import sys

# Dynamic root folder injection layer to completely prevent ModuleNotFoundError on Streamlit Cloud
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# Safe local package imports
from core.compliance_filter import ComplianceFilter
from core.risk_engine import ComplianceRiskEngine
from core.explainability import UnderwritingExplainer
from core.audit_logger import ImmutableAuditLogger
from core.report_generator import ComplianceReportGenerator

st.set_page_config(page_title="CreditPulse-AI | NBFC Audit Portfolio Sandbox", layout="wide")

# Dashboard Headers
st.markdown("<h2 style='color:#1E3A8A;'>CreditPulse-AI: NBFC Risk Intelligence Pipeline</h2>", unsafe_allow_html=True)
st.write("Dynamic RBI portfolio auditing, multi-asset scorecards, and regulatory compliance logging.")

# Multi-Mode Model Initialization Engine
@st.cache_resource
def load_underwriting_model():
    X_mock = np.random.rand(10, 5)
    y_mock = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    fallback_model = RandomForestClassifier(n_estimators=10, random_state=42)
    fallback_model.fit(X_mock, y_mock)
    return fallback_model

model = load_underwriting_model()

# Core Services Instantiation
cleaner = ComplianceFilter()
engine = ComplianceRiskEngine(model)
logger = ImmutableAuditLogger()

# 1. Provide a Quick Download for a Test CSV Template
st.markdown("### 🛠️ Ingestion Control Center")
sample_data = pd.DataFrame({
    'account_id': ['ACC-101', 'ACC-102', 'ACC-103', 'ACC-104', 'ACC-105'],
    'product_type': ['home_loan', 'gold_loan', 'bike_loan', 'credit_card', 'personal_loan'],
    'loan_amount':,
    'bureau_score':,
    'monthly_income':,
    'ltv_ratio': [0.65, 0.79, 0.85, 0.00, 0.00],  # Note ACC-102 intentionally breaches the RBI 75% gold LTV limit
    'religion': ['Non-Disclosed', 'Non-Disclosed', 'Non-Disclosed', 'Non-Disclosed', 'Non-Disclosed'] # Restricted Data
})

st.download_button(
    label="⬇️ Download Sample NBFC Multi-Loan CSV Dataset",
    data=sample_data.to_csv(index=False),
    file_name="nbfc_portfolio_sample.csv",
    mime="text/csv"
)

# 2. File Upload Interface Layer
uploaded_file = st.file_uploader("Upload Active Portfolio Transaction Ledger Document", type=["csv"])

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    
    # Execute Demographic Bias Audit Scans
    cleaned_df, stripped_cols = cleaner.audit_and_clean(raw_df)
    if stripped_cols:
        st.info(f"🛡️ **RBI Fair Practice Filter Active**: Extracted non-permissible features from evaluation modeling: {stripped_cols}")
        
    if 'loan_amount' in cleaned_df.columns and 'account_id' in cleaned_df.columns:
        # Run analytical evaluation calculations across the portfolio
        results = engine.calculate_ecl(cleaned_df.drop(columns=['account_id']), 'loan_amount')
        results['account_id'] = cleaned_df['account_id'].astype(str)
        
        # Product type dynamic filters UI
        available_segments = list(results['product_type'].unique())
        selected_segments = st.multiselect("🎛️ Filter View by Asset Segment Profile:", available_segments, default=available_segments)
        
        filtered_results = results[results['product_type'].isin(selected_segments)]
        
        # --- UI LAYOUT SECTION 1: VISUAL ANALYTICS ---
        st.markdown("### 📊 Portfolio Analytics Workbench")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pd = px.histogram(
                filtered_results, x="Probability_of_Default_PD", color="Risk_Classification",
                title="Portfolio Probability of Default (PD) Profile Dispersion",
                color_discrete_map={"Healthy (Good)": "#10B981", "High Risk (Bad)": "#EF4444", "CRITICAL BREACH: LTV > 75%": "#7C3AED"}
            )
            st.plotly_chart(fig_pd, use_container_width=True)
            
        with col2:
            fig_ecl = px.box(
                filtered_results, x="product_type", y="Expected_Credit_Loss_ECL", color="Risk_Classification",
                title="Expected Credit Loss (ECL) Risk Exposure by Product Line",
                color_discrete_map={"Healthy (Good)": "#10B981", "High Risk (Bad)": "#EF4444", "CRITICAL BREACH: LTV > 75%": "#7C3AED"}
            )
            st.plotly_chart(fig_ecl, use_container_width=True)
            
        st.subheader("📋 Active Asset Evaluation Ledger Summary")
        st.dataframe(filtered_results[['account_id', 'product_type', 'Probability_of_Default_PD', 'Expected_Credit_Loss_ECL', 'Risk_Classification']], use_container_width=True)
        
        # --- UI LAYOUT SECTION 2: CLIENT REJECTION REASON CODE EXPLORER ---
        st.markdown("---")
        st.markdown("### 🔍 Individual Audit Workbench & Key Fact Statement (KFS) Analyzer")
        
        selected_id = st.selectbox("Select Target Account ID for review:", filtered_results['account_id'].unique())
        
        client_metrics = filtered_results[filtered_results['account_id'] == selected_id].iloc[0]
        target_row = cleaned_df[cleaned_df['account_id'].astype(str) == selected_id].drop(columns=['account_id'])
        
        # Process SHAP proxy values
        explainer = UnderwritingExplainer(model, cleaned_df.drop(columns=['account_id']))
        feature_weights = explainer.generate_force_plot_data(target_row)
        
        features_df = pd.DataFrame({
            'Underwriting Factor Metric': list(feature_weights.keys()),
            'Risk Contribution Weight': list(feature_weights.values())
        }).sort_values(by="Risk Contribution Weight")
        
        features_df['Color'] = features_df['Risk Contribution Weight'].apply(lambda x: '#EF4444' if x > 0 else '#10B981')
        
        fig_weights = go.Figure(go.Bar(
            x=features_df['Risk Contribution Weight'], y=features_df['Underwriting Factor Metric'],
            orientation='h', marker_color=features_df['Color']
        ))
        fig_weights.update_layout(title=f"Explainable AI Reason Codes (RBI Transparency Rule) for {selected_id}", template="plotly_white", height=300)
        st.plotly_chart(fig_weights, use_container_width=True)
        
        if st.button(f"Generate & Freeze Statutory PDF Audit Report for Account {selected_id}"):
            pdf_path = ComplianceReportGenerator.generate_pdf(
                selected_id, client_metrics['Probability_of_Default_PD'], 
                client_metrics['Expected_Credit_Loss_ECL'], client_metrics['Risk_Classification'], feature_weights
            )
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download Official Compliance Audit Document", data=f, file_name=f"Report_{selected_id}.pdf", mime="application/pdf")
            st.success(f"Audit log frozen locally at: {pdf_path}")
    else:
        st.error("Invalid File Format. Upload a CSV file matching the schema headers provided above.")
