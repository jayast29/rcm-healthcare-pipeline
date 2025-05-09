## 🩺 RCM - Healthcare Streamlit Dashboard

This project presents **Streamlit Dashboard** for Revenue Cycle Management (RCM) in healthcare.


### 🚀 Project Summary

An end-to-end Azure Data Engineering pipeline was implemented to support healthcare RCM analytics. Data was ingested from multiple sources including.
- **Azure SQL DB** for EMR data
- **Flat files** for claims
- **APIs** for NPI and ICD code enrichment

A **medallion architecture** was used in **ADLS Gen2**, with ingestion orchestrated via **Azure Data Factory**. Data transformation and processing was done in **Azure Databricks**.

The refined **Gold Layer** produced analytical fact and dimension tables, which powered this interactive Streamlit dashboard showing KPIs.

### 📊 Features in the Dashboard

- 📄 **Overview** – Project summary + KPI metrics
 ![Dashboard Overview](visualizations/0_overview.png)

- 📈 **Revenue Trends** – Charges, payments & outstanding over time
![Visualization](visualizations/1_revenue_trends.png)
 
- ⌛ **AR Aging Overview** – Avg. Days in AR by bucket
![Visualization](visualizations/2_ar_aging.png)
 
- 🏥 **Outstanding by Department** – Top departments by AR
![Visualization](visualizations/3_outstanding_revenue.png)
  
- 💰 **Top Procedures by Charge** – Highest revenue-generating procedures
![Visualization](visualizations/4_top_procedure.png)
  
- 🧍‍♀️ **Patient Distribution by Department** – Gender-based patient counts
![Visualization](visualizations/5_patient_distribution.png)
  
- 💳 **Payment Types** – Payment distribution by payer type
![Visualization](visualizations/6_payment_type.png)
 
- 🩺 **Visit Type Impact** – Financial metrics by visit type
![Visualization](visualizations/7_visit_type.png)


