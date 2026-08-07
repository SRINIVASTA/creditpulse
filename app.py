import os
import sys

# =====================================================================
# 1. PATH RESOLUTION LAYER (Fixes ModuleNotFoundError)
# =====================================================================
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

from core.compliance_filter import ComplianceFilter
from core.risk_engine import ComplianceRiskEngine
from core.explainability import UnderwritingExplainer
from core.audit_logger import ImmutableAuditLogger
from core.report_generator import ComplianceReportGenerator

st.set_page_config(page_title="CreditPulse-AI | NBFC Regulatory Audit Engine", layout="wide")

st.markdown("<h2 style='color:#1E3A8A;'>CreditPulse-AI: NBFC Regulatory Audit Dashboard</h2>", unsafe_allow_html=True)
st.write("Statutory Asset Classification, Provisioning Reserves Tracker, and Capital Adequacy Controls.")

@st.cache_resource
def load_underwriting_model():
    X_mock = np.random.rand(10, 5)
    y_mock = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    fallback_model = RandomForestClassifier(n_estimators=10, random_state=42)
    fallback_model.fit(X_mock, y_mock)
    return fallback_model

model = load_underwriting_model()
cleaner = ComplianceFilter()
engine = ComplianceRiskEngine(model)

# =====================================================================
# 2. VALIDATED INLINE DATASETS SYSTEM (Completely populated)
# =====================================================================
st.markdown("### 🛠️ Data Ingestion Desk")
sample_data = pd.DataFrame({
    'account_id': ['HL-901', 'GL-902', 'BL-903', 'CC-904', 'PL-905'],
    'product_type': ['home_loan', 'gold_loan', 'bike_loan', 'credit_card', 'personal_loan'],
    'loan_amount': [4500000.0, 300000.0, 120000.0, 250000.0, 500000.0],
    'bureau_score':,
    'monthly_income': [115000.0, 48000.0, 28000.0, 85000.0, 55000.0],
    'debt_to_income': [0.42, 0.25, 0.30, 0.15, 0.55],
    'ltv_ratio': [0.65, 0.79, 0.85, 0.00, 0.00],
    'collateral_val': [6900000.0, 380000.0, 140000.0, 0.0, 0.0],
    'religion': ['Non-Disclosed', 'Non-Disclosed', 'Non-Disclosed', 'Non-Disclosed', 'Non-Disclosed']
})

st.download_button(
    label="⬇️ Download RBI-Compliant Multi-Asset Schema Template",
    data=sample_data.to_csv(index=False),
    file_name="rbi_nbfc_schema.csv",
    mime="text/csv"
)

uploaded_file = st.file_uploader("Upload Core Banking Portfolio CSV Ledger", type=["csv"])

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    cleaned_df, stripped_cols = cleaner.audit_and_clean(raw_df)
    
    if stripped_cols:
        st.info(f"🛡️ **RBI Fair Practice Filter Active**: Cleaned restricted columns from data stack: {stripped_cols}")
        
    if 'loan_amount' in cleaned_df.columns and 'account_id' in cleaned_df.columns:
        results = engine.calculate_ecl(cleaned_df.drop(columns=['account_id']), 'loan_amount')
        results['account_id'] = cleaned_df['account_id'].astype(str)
        
        # =====================================================================
        # 3. STATUTORY TOP TRACKER BANNER LAYER (Capital Adequacy & CRAR Sandbox)
        # =====================================================================
        st.markdown("### 🏛️ Capital Adequacy & Reserve Provisioning Tracker")
        
        total_portfolio_ead = results['EAD'].sum()
        total_provisions_required = results['RBI_Mandated_Provision'].sum()
        total_rwa = results['RWA'].sum()
        
        # Simulate NBFC Core Owned Capital Tier for CRAR illustration
        nbfc_own_tier1_capital = 12000000.0  # ₹1.2 Crore Mock Base Capital Buffer
        computed_crar = (nbfc_own_tier1_capital / total_rwa) * 100 if total_rwa > 0 else 100.0
        
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.metric("Total Exposure (EAD)", f"₹{total_portfolio_ead:,.2f}")
        with kpi_col2:
            st.metric("RBI Mandated Provisions Pool", f"₹{total_provisions_required:,.2f}", delta="- Profit & Loss", delta_color="inverse")
        with kpi_col3:
            st.metric("Risk Weighted Assets (RWA)", f"₹{total_rwa:,.2f}")
        with kpi_col4:
            status_tag = "✅ COMPLIANT" if computed_crar >= 15.0 else "⚠️ CAPITAL DEFICIT"
            st.metric("Capital Adequacy Ratio (CRAR)", f"{computed_crar:.2f}%", status_tag)
            
        st.markdown("---")
        
        # --- PORTFOLIO DYNAMIC SEGMENT INTERACTION ---
        available_products = list(results['product_type'].unique())
        selected_segments = st.multiselect("🎛️ Select Active Audit Portfolios:", available_products, default=available_products)
        filtered_results = results[results['product_type'].isin(selected_segments)]
        
        # --- VISUAL ANALYTICS ---
        st.markdown("### 📊 Portfolio Asset Classification Profiler")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pd = px.histogram(
                filtered_results, x="Risk_Classification", y="RBI_Mandated_Provision", color="product_type",
                title="Statutory Provision Burden Distribution by RBI Bucket Status",
                labels={"Risk_Classification": "RBI Asset Category", "RBI_Mandated_Provision": "Required Provisions (₹)"},
                template="plotly_white"
            )
            st.plotly_chart(fig_pd, use_container_width=True)
            
        with col2:
            fig_ecl = px.scatter(
                filtered_results, x="EAD", y="RBI_Mandated_Provision", color="Risk_Classification", size="RWA",
                title="Exposure vs Mandated Provision Weight Projections",
                labels={"EAD": "Exposure at Default", "RBI_Mandated_Provision": "Required Reserves"},
                template="plotly_white"
            )
            st.plotly_chart(fig_ecl, use_container_width=True)
            
        st.subheader("📋 Centralized Asset Regulatory Grading Registry")
        st.dataframe(
            filtered_results[['account_id', 'product_type', 'EAD', 'Secured_Exposure', 'Unsecured_Exposure', 'RBI_Mandated_Provision', 'RWA', 'Risk_Classification']], 
            use_container_width=True
        )
        
        # --- INDIVIDUAL CLIENT EXPLORER ---
        st.markdown("---")
        st.markdown("### 🔍 Granular Account Audit Trail")
        selected_id = st.selectbox("Select Target Account ID for review:", filtered_results['account_id'].unique())
        
        client_metrics = filtered_results[filtered_results['account_id'] == selected_id].iloc[0]
        target_row = cleaned_df[cleaned_df['account_id'].astype(str) == selected_id].drop(columns=['account_id'])
        
        explainer = UnderwritingExplainer(model, cleaned_df.drop(columns=['account_id']))
        feature_weights = explainer.generate_force_plot_data(target_row)
        
        features_df = pd.DataFrame({
            'Underwriting Metric Factor': list(feature_weights.keys()),
            'Risk Weight Attribution': list(feature_weights.values())
        }).sort_values(by="Risk Weight Attribution")
        features_df['Color'] = features_df['Risk Weight Attribution'].apply(lambda x: '#EF4444' if x > 0 else '#10B981')
        
        fig_weights = go.Figure(go.Bar(
            x=features_df['Risk Weight Attribution'], y=features_df['Underwriting Metric Factor'],
            orientation='h', marker_color=features_df['Color']
        ))
        fig_weights.update_layout(title=f"Reason Codes Attribution Weights for Account: {selected_id}", template="plotly_white", height=300)
        st.plotly_chart(fig_weights, use_container_width=True)
        
        if st.button(f"Compile Regulatory Audit Records for Account {selected_id}"):
            pdf_path = ComplianceReportGenerator.generate_pdf(
                selected_id, client_metrics['Probability_of_Default_PD'], 
                client_metrics['RBI_Mandated_Provision'], client_metrics['Risk_Classification'], feature_weights
            )
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download Official Compliance Audit Document", data=f, file_name=f"Report_{selected_id}.pdf", mime="application/pdf")
            st.success(f"Audit log frozen locally at: {pdf_path}")
    else:
        st.error("Invalid File Format. Upload a CSV file matching the schema headers provided above.")
