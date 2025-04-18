# Databricks notebook source
from pyspark.sql import SparkSession, functions as f

#Reading Hospital A departments data 
df_hosa=spark.read.parquet("/mnt/bronze/hosa/transactions")

#Reading Hospital B departments data 
df_hosb=spark.read.parquet("/mnt/bronze/hosb/transactions")

#union two departments dataframes
df_merged = df_hosa.unionByName(df_hosb)
display(df_merged)

df_merged.createOrReplaceTempView("transactions")


# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW quality_checks AS
# MAGIC SELECT 
# MAGIC concat(TransactionID,'-',Datasource) as TransactionID,
# MAGIC TransactionID as SRC_TransactionID,
# MAGIC EncounterID,
# MAGIC PatientID,
# MAGIC ProviderID,
# MAGIC DeptID,
# MAGIC VisitDate,
# MAGIC ServiceDate,
# MAGIC PaidDate,
# MAGIC VisitType,
# MAGIC Amount,
# MAGIC AmountType,
# MAGIC PaidAmount,
# MAGIC ClaimID,
# MAGIC PayorID,
# MAGIC ProcedureCode,
# MAGIC ICDCode,
# MAGIC LineOfBusiness,
# MAGIC MedicaidID,
# MAGIC MedicareID,
# MAGIC InsertDate as SRC_InsertDate,
# MAGIC ModifiedDate as SRC_ModifiedDate,
# MAGIC Datasource,
# MAGIC     CASE 
# MAGIC         WHEN EncounterID IS NULL OR PatientID IS NULL OR TransactionID IS NULL OR VisitDate IS NULL THEN TRUE
# MAGIC         ELSE FALSE
# MAGIC     END AS is_quarantined
# MAGIC FROM transactions

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS silver.transactions (
# MAGIC   TransactionID string,
# MAGIC   SRC_TransactionID string,
# MAGIC   EncounterID string,
# MAGIC   PatientID string,
# MAGIC   ProviderID string,
# MAGIC   DeptID string,
# MAGIC   VisitDate date,
# MAGIC   ServiceDate date,
# MAGIC   PaidDate date,
# MAGIC   VisitType string,
# MAGIC   Amount double,
# MAGIC   AmountType string,
# MAGIC   PaidAmount double,
# MAGIC   ClaimID string,
# MAGIC   PayorID string,
# MAGIC   ProcedureCode integer,
# MAGIC   ICDCode string,
# MAGIC   LineOfBusiness string,
# MAGIC   MedicaidID string,
# MAGIC   MedicareID string,
# MAGIC   SRC_InsertDate date,
# MAGIC   SRC_ModifiedDate date,
# MAGIC   Datasource string,
# MAGIC   is_quarantined boolean,
# MAGIC   audit_insertdate timestamp,
# MAGIC   audit_modifieddate timestamp,
# MAGIC   is_current boolean
# MAGIC )
# MAGIC USING DELTA;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Update old record to implement SCD Type 2
# MAGIC MERGE INTO silver.transactions AS target USING quality_checks AS source ON target.TransactionID = source.TransactionID
# MAGIC AND target.is_current = true
# MAGIC WHEN MATCHED
# MAGIC AND (
# MAGIC   target.SRC_TransactionID != source.SRC_TransactionID
# MAGIC   OR target.EncounterID != source.EncounterID
# MAGIC   OR target.PatientID != source.PatientID
# MAGIC   OR target.ProviderID != source.ProviderID
# MAGIC   OR target.DeptID != source.DeptID
# MAGIC   OR target.VisitDate != source.VisitDate
# MAGIC   OR target.ServiceDate != source.ServiceDate
# MAGIC   OR target.PaidDate != source.PaidDate
# MAGIC   OR target.VisitType != source.VisitType
# MAGIC   OR target.Amount != source.Amount
# MAGIC   OR target.AmountType != source.AmountType
# MAGIC   OR target.PaidAmount != source.PaidAmount
# MAGIC   OR target.ClaimID != source.ClaimID
# MAGIC   OR target.PayorID != source.PayorID
# MAGIC   OR target.ProcedureCode != source.ProcedureCode
# MAGIC   OR target.ICDCode != source.ICDCode
# MAGIC   OR target.LineOfBusiness != source.LineOfBusiness
# MAGIC   OR target.MedicaidID != source.MedicaidID
# MAGIC   OR target.MedicareID != source.MedicareID
# MAGIC   OR target.SRC_InsertDate != source.SRC_InsertDate
# MAGIC   OR target.SRC_ModifiedDate != source.SRC_ModifiedDate
# MAGIC   OR target.Datasource != source.Datasource
# MAGIC   OR target.is_quarantined != source.is_quarantined
# MAGIC ) THEN
# MAGIC UPDATE
# MAGIC SET
# MAGIC   target.is_current = false,
# MAGIC   target.audit_modifieddate = current_timestamp()

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Step 0: Disable ANSI mode to prevent casting errors
# MAGIC SET spark.sql.ansi.enabled = false;
# MAGIC
# MAGIC -- Step 1: Merge for SCD Type 2 with explicit date parsing
# MAGIC MERGE INTO silver.transactions AS target
# MAGIC USING quality_checks AS source
# MAGIC ON target.TransactionID = source.TransactionID
# MAGIC AND target.is_current = true
# MAGIC
# MAGIC WHEN NOT MATCHED THEN
# MAGIC INSERT (
# MAGIC   TransactionID,
# MAGIC   SRC_TransactionID,
# MAGIC   EncounterID,
# MAGIC   PatientID,
# MAGIC   ProviderID,
# MAGIC   DeptID,
# MAGIC   VisitDate,
# MAGIC   ServiceDate,
# MAGIC   PaidDate,
# MAGIC   VisitType,
# MAGIC   Amount,
# MAGIC   AmountType,
# MAGIC   PaidAmount,
# MAGIC   ClaimID,
# MAGIC   PayorID,
# MAGIC   ProcedureCode,
# MAGIC   ICDCode,
# MAGIC   LineOfBusiness,
# MAGIC   MedicaidID,
# MAGIC   MedicareID,
# MAGIC   SRC_InsertDate,
# MAGIC   SRC_ModifiedDate,
# MAGIC   Datasource,
# MAGIC   is_quarantined,
# MAGIC   audit_insertdate,
# MAGIC   audit_modifieddate,
# MAGIC   is_current
# MAGIC )
# MAGIC VALUES (
# MAGIC   source.TransactionID,
# MAGIC   source.SRC_TransactionID,
# MAGIC   source.EncounterID,
# MAGIC   source.PatientID,
# MAGIC   source.ProviderID,
# MAGIC   source.DeptID,
# MAGIC   TO_DATE(source.VisitDate, 'M/d/yyyy'),
# MAGIC   TO_DATE(source.ServiceDate, 'M/d/yyyy'),
# MAGIC   TO_DATE(source.PaidDate, 'M/d/yyyy'),
# MAGIC   source.VisitType,
# MAGIC   source.Amount,
# MAGIC   source.AmountType,
# MAGIC   source.PaidAmount,
# MAGIC   source.ClaimID,
# MAGIC   source.PayorID,
# MAGIC   source.ProcedureCode,
# MAGIC   source.ICDCode,
# MAGIC   source.LineOfBusiness,
# MAGIC   source.MedicaidID,
# MAGIC   source.MedicareID,
# MAGIC   TO_TIMESTAMP(source.SRC_InsertDate, 'M/d/yyyy'),
# MAGIC   TO_TIMESTAMP(source.SRC_ModifiedDate, 'M/d/yyyy'),
# MAGIC   source.Datasource,
# MAGIC   source.is_quarantined,
# MAGIC   current_timestamp(),
# MAGIC   current_timestamp(),
# MAGIC   true
# MAGIC );
# MAGIC