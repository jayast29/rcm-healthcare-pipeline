import streamlit as st
import pandas as pd
import plotly.express as px

# Set Streamlit page config
st.set_page_config(page_title="RCM Healthcare Dashboard", layout="wide")

# Title of the dashboard
st.title("🩺 Revenue Cycle Management - Healthcare Dashboard")

# Load data
df = pd.read_csv("rcm_data.csv", parse_dates=["ServiceDate", "PaidDate"], dayfirst=False)

# Sidebar navigation
selected_tab = st.sidebar.radio(
    "📊 Select a view:",
    [
        "📄 Overview",
        "📈 Revenue Trends",
        "⏳ AR Aging Overview",
        "🏬 Outstanding by Department",
        "💰 Top Procedures by Charge",
        "👥 Patient Distribution by Department",
        "💳 Payment Types",
        "🧾 Visit Type Impact"
    ]
)

# 📄 Overview
if selected_tab == "📄 Overview":
    st.header("📄 Overview")

    st.markdown("""
    <div style="font-size: 20px; line-height: 1.6;">
        This dashboard presents an end-to-end analytics layer for Revenue Cycle Management (RCM) in healthcare, built on a modern data engineering stack. 
        It integrates data from multiple sources, including EMR systems via Azure SQL Database, flat files for claims, and APIs for provider and diagnosis codes. 
        A medallion architecture in ADLS Gen2 supports data refinement across bronze, silver, and gold layers. Metadata-driven pipelines in Azure Data Factory 
        orchestrate ingestion, while Azure Databricks handles processing using Delta Lake with SCD2 logic and Common Data Model (CDM) structures. 
        The refined Gold layer powers KPIs like <i>Days in AR</i> and <i>Percentage AR > 90 Days</i>. Best practices such as Key Vault integration, 
        Unity Catalog for governance, and parallelized pipelines ensure security, scalability, and maintainability. 
        This Streamlit dashboard delivers a visual, interactive experience for exploring RCM performance metrics.
    </div>
    <br><br><br>
    """, unsafe_allow_html=True)

    total_charges = df["Charge_Amount"].sum()
    total_paid = df["Paid_Amount"].sum()
    total_outstanding = df["Outstanding_Amount"].sum()
    total_claims = df["ClaimID"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Charges", f"${total_charges:,.2f}")
    col2.metric("✅ Total Paid", f"${total_paid:,.2f}")
    col3.metric("📉 Outstanding Amount", f"${total_outstanding:,.2f}")
    col4.metric("📄 Total Claims", total_claims)

# 📈 Revenue Trends
elif selected_tab == "📈 Revenue Trends":
    st.header("📈 Revenue Trends Over Time")
    st.write("Visualize how charges, payments, and outstanding balances have changed over months.")

    df["Month"] = df["ServiceDate"].dt.to_period("M").astype(str)
    monthly_revenue = df.groupby("Month")[["Charge_Amount", "Paid_Amount", "Outstanding_Amount"]].sum().reset_index()

    fig = px.line(monthly_revenue, x="Month", y=["Charge_Amount", "Paid_Amount", "Outstanding_Amount"],
                  title="Monthly Revenue, Payments, and Outstanding Amounts")
    st.plotly_chart(fig, use_container_width=True)

# ⏳ AR Aging Overview
elif selected_tab == "⏳ AR Aging Overview":
    st.header("⏳ AR Aging Overview by Bucket")
    st.write("Understand the average number of days receivables are pending, broken down by AR buckets.")

    ar_bucket_summary = df.groupby("AR_Bucket")["Days_in_AR"].mean().reset_index()
    fig = px.bar(ar_bucket_summary, x="AR_Bucket", y="Days_in_AR", color="AR_Bucket",
                 labels={"Days_in_AR": "Avg Days in AR"}, title="Average Days in AR by Bucket")
    st.plotly_chart(fig)

# 🏬 Outstanding by Department
elif selected_tab == "🏬 Outstanding by Department":
    st.header("🏬 Outstanding Amount by Department")
    st.write("Explore which departments have the highest outstanding balances.")

    dept_outstanding = df.groupby("Department_Name")["Outstanding_Amount"].sum().reset_index()
    dept_outstanding = dept_outstanding.sort_values("Outstanding_Amount", ascending=False)
    fig = px.bar(dept_outstanding, x="Outstanding_Amount", y="Department_Name", orientation="h",
                 title="Total Outstanding Amount by Department", labels={"Outstanding_Amount": "Outstanding ($)"})
    st.plotly_chart(fig)

# 💰 Top Procedures by Charge
elif selected_tab == "💰 Top Procedures by Charge":
    st.header("💰 Top Procedures by Charge")
    st.write("See which procedures generate the most revenue based on charge amount.")

    top_procs = df.groupby("ProcedureCode")["Charge_Amount"].sum().reset_index()
    top_procs = top_procs.sort_values("Charge_Amount", ascending=False).head(10)
    fig = px.bar(top_procs, x="ProcedureCode", y="Charge_Amount", color="Charge_Amount",
                 title="Top 10 Procedures by Charge Amount", labels={"Charge_Amount": "Total Charges ($)"})
    st.plotly_chart(fig)

# 👥 Patient Distribution by Department
elif selected_tab == "👥 Patient Distribution by Department":
    st.header("👥 Patient Gender Distribution by Department")
    st.write("Understand the gender distribution of patients across different hospital departments.")

    gender_dept = df.groupby(["Department_Name", "Patient_Gender"]).size().reset_index(name="Count")
    fig = px.bar(
        gender_dept,
        x="Department_Name",
        y="Count",
        color="Patient_Gender",
        title="Patient Gender Distribution Across Departments",
        labels={"Count": "Number of Patients", "Department_Name": "Department"},
        barmode="stack"
    )
    fig.update_layout(
        xaxis_title="Department",
        yaxis_title="Number of Patients",
        xaxis_tickangle=90
    )
    st.plotly_chart(fig)

# 💳 Payment Types
elif selected_tab == "💳 Payment Types":
    st.header("💳 Distribution of Payment Types")
    st.write("Analyze how different payment types contribute to the total paid amounts.")

    amt_types = df.groupby("AmountType")["Paid_Amount"].sum().reset_index()
    fig = px.pie(amt_types, names="AmountType", values="Paid_Amount",
                 title="Payment Amount Distribution by Payer Type")
    st.plotly_chart(fig)

# 🧾 Visit Type Impact
elif selected_tab == "🧾 Visit Type Impact":
    st.header("🧾 Visit Type Impact on Financials")
    st.write("Compare financial metrics across different visit types like inpatient, outpatient, etc.")

    visit_data = df.groupby("VisitType")[["Charge_Amount", "Paid_Amount", "Outstanding_Amount"]].sum().reset_index()
    fig = px.bar(visit_data, x="VisitType", y=["Charge_Amount", "Paid_Amount", "Outstanding_Amount"],
                 barmode="group", title="Visit Type vs Financial Metrics")
    st.plotly_chart(fig)
