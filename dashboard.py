import streamlit as st
import pandas as pd
from database import SessionLocal, LogEntry

st.set_page_config(
    page_title="RedCheck Enterprise Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Clean modern visual style
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# Header with Logo and Title
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("logo.png", width=90)
    except:
        st.markdown("🛡️")

with col_title:
    st.title("RedCheck Enterprise Intelligence Dashboard")
    st.caption("Real-time LLM Telemetry, Hallucination Prevention & Financial Risk Mitigation")

st.markdown("---")

# Load data from the database
db = SessionLocal()
logs = db.query(LogEntry).all()
db.close()

if not logs:
    st.info("No telemetry logs found in the database yet. Run your test script to ingest data.")
else:
    # Process data for UI
    data = []
    for log in logs:
        payload = log.raw_payload or {}
        eval_data = payload.get("evaluation", {})
        business_impact = eval_data.get("business_impact", {})
        
        data.append({
            "ID": log.id,
            "Trace ID": log.trace_id,
            "Status": log.status,
            "Risk (USD)": log.risk_usd or business_impact.get("risk_usd", 0.0),
            "Severity": business_impact.get("severity", "N/A"),
            "Category": business_impact.get("category", "N/A"),
            "Timestamp": log.timestamp
        })
    
    df = pd.DataFrame(data)

    # --- TOP METRICS (KPIs) ---
    total_logs = len(df)
    total_risk = df["Risk (USD)"].sum()
    failures = len(df[df["Status"] != "SUCCESS"])

    m1, m2, m3 = st.columns(3)
    m1.metric("Total LLM Requests", total_logs)
    m2.metric("Mitigated Financial Risk", f"${total_risk:,.2f}")
    m3.metric("Alerts / Failures", failures, delta_color="inverse" if failures > 0 else "off")

    st.markdown("### 📊 Risk & Telemetry Analysis")

    # --- VISUAL CHARTS ---
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Request Status")
        status_counts = df["Status"].value_counts()
        st.bar_chart(status_counts)

    with g2:
        st.subheader("Risk (USD) by Category")
        if "Category" in df.columns and df["Risk (USD)"].sum() > 0:
            category_risk = df.groupby("Category")["Risk (USD)"].sum()
            st.bar_chart(category_risk)
        else:
            st.info("Insufficient data for risk by category.")

    st.markdown("### 📋 Detailed Event Log")
    
    # --- CLEAN STRUCTURED TABLE ---
    st.dataframe(
        df[["ID", "Trace ID", "Status", "Severity", "Category", "Risk (USD)", "Timestamp"]],
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.caption("RedCheck Security Framework v0.5.0 | Enterprise Production Environment")
