# Databricks notebook source
# MAGIC %sql
# MAGIC -- Create temporary views for the parquet files
# MAGIC CREATE OR REPLACE TEMP VIEW hosa_encounters
# MAGIC USING parquet
# MAGIC OPTIONS (
# MAGIC   path "dbfs:/mnt/bronze/hosa/encounters"
# MAGIC );
# MAGIC
# MAGIC CREATE OR REPLACE TEMP VIEW hosb_encounters
# MAGIC USING parquet
# MAGIC OPTIONS (
# MAGIC   path "dbfs:/mnt/bronze/hosb/encounters"
# MAGIC );
# MAGIC
# MAGIC -- Union the two views
# MAGIC CREATE OR REPLACE TEMP VIEW encounters AS
# MAGIC SELECT * FROM hosa_encounters
# MAGIC UNION ALL
# MAGIC SELECT * FROM hosb_encounters;
# MAGIC
# MAGIC -- Display the merged data
# MAGIC SELECT * FROM encounters;

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from encounters

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW quality_checks AS
# MAGIC SELECT 
# MAGIC concat(EncounterID,'-',Datasource) as EncounterID,
# MAGIC EncounterID SRC_EncounterID,
# MAGIC PatientID,
# MAGIC EncounterDate,
# MAGIC EncounterType,
# MAGIC ProviderID,
# MAGIC DepartmentID,
# MAGIC ProcedureCode,
# MAGIC InsertedDate as SRC_InsertedDate,
# MAGIC ModifiedDate as SRC_ModifiedDate,
# MAGIC Datasource,
# MAGIC     CASE 
# MAGIC         WHEN EncounterID IS NULL OR PatientID IS NULL THEN TRUE
# MAGIC         ELSE FALSE
# MAGIC     END AS is_quarantined
# MAGIC FROM encounters

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from quality_checks
# MAGIC where Datasource='hosb'

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS silver.encounters (
# MAGIC EncounterID string,
# MAGIC SRC_EncounterID string,
# MAGIC PatientID string,
# MAGIC EncounterDate date,
# MAGIC EncounterType string,
# MAGIC ProviderID string,
# MAGIC DepartmentID string,
# MAGIC ProcedureCode integer,
# MAGIC SRC_InsertedDate date,
# MAGIC SRC_ModifiedDate date,
# MAGIC Datasource string,
# MAGIC is_quarantined boolean,
# MAGIC audit_insertdate timestamp,
# MAGIC audit_modifieddate timestamp,
# MAGIC is_current boolean
# MAGIC )
# MAGIC USING DELTA;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Step 0: Disable ANSI mode to avoid CAST errors
# MAGIC SET spark.sql.ansi.enabled = false;
# MAGIC
# MAGIC -- Step 1: Update old record to implement SCD Type 2 with explicit date casting
# MAGIC MERGE INTO silver.encounters AS target
# MAGIC USING quality_checks AS source
# MAGIC ON target.EncounterID = source.EncounterID AND target.is_current = true
# MAGIC
# MAGIC WHEN MATCHED AND (
# MAGIC     target.SRC_EncounterID != source.SRC_EncounterID OR
# MAGIC     target.PatientID != source.PatientID OR
# MAGIC     target.EncounterDate != TO_DATE(source.EncounterDate, 'M/d/yyyy') OR
# MAGIC     target.EncounterType != source.EncounterType OR
# MAGIC     target.ProviderID != source.ProviderID OR
# MAGIC     target.DepartmentID != source.DepartmentID OR
# MAGIC     target.ProcedureCode != source.ProcedureCode OR
# MAGIC     target.SRC_InsertedDate != TO_TIMESTAMP(source.SRC_InsertedDate, 'M/d/yyyy') OR
# MAGIC     target.SRC_ModifiedDate != TO_TIMESTAMP(source.SRC_ModifiedDate, 'M/d/yyyy') OR
# MAGIC     target.Datasource != source.Datasource OR
# MAGIC     target.is_quarantined != source.is_quarantined
# MAGIC ) THEN
# MAGIC   UPDATE SET
# MAGIC     target.is_current = false,
# MAGIC     target.audit_modifieddate = current_timestamp();
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Step 0: Disable ANSI mode to avoid CAST errors
# MAGIC SET spark.sql.ansi.enabled = false;
# MAGIC
# MAGIC -- Step 1: Update old record to implement SCD Type 2 with explicit date casting
# MAGIC MERGE INTO silver.encounters AS target
# MAGIC USING quality_checks AS source
# MAGIC ON target.EncounterID = source.EncounterID AND target.is_current = true
# MAGIC
# MAGIC WHEN MATCHED AND (
# MAGIC     target.SRC_EncounterID != source.SRC_EncounterID OR
# MAGIC     target.PatientID != source.PatientID OR
# MAGIC     target.EncounterDate != TO_DATE(source.EncounterDate, 'M/d/yyyy') OR
# MAGIC     target.EncounterType != source.EncounterType OR
# MAGIC     target.ProviderID != source.ProviderID OR
# MAGIC     target.DepartmentID != source.DepartmentID OR
# MAGIC     target.ProcedureCode != source.ProcedureCode OR
# MAGIC     target.SRC_InsertedDate != TO_TIMESTAMP(source.SRC_InsertedDate, 'M/d/yyyy') OR
# MAGIC     target.SRC_ModifiedDate != TO_TIMESTAMP(source.SRC_ModifiedDate, 'M/d/yyyy') OR
# MAGIC     target.Datasource != source.Datasource OR
# MAGIC     target.is_quarantined != source.is_quarantined
# MAGIC )
# MAGIC THEN
# MAGIC   UPDATE SET
# MAGIC     target.is_current = false,
# MAGIC     target.audit_modifieddate = current_timestamp()
# MAGIC
# MAGIC -- Step 2: Insert new version of the record
# MAGIC WHEN NOT MATCHED
# MAGIC THEN INSERT (
# MAGIC     EncounterID,
# MAGIC     SRC_EncounterID,
# MAGIC     PatientID,
# MAGIC     EncounterDate,
# MAGIC     EncounterType,
# MAGIC     ProviderID,
# MAGIC     DepartmentID,
# MAGIC     ProcedureCode,
# MAGIC     SRC_InsertedDate,
# MAGIC     SRC_ModifiedDate,
# MAGIC     Datasource,
# MAGIC     is_quarantined,
# MAGIC     audit_insertdate,
# MAGIC     audit_modifieddate,
# MAGIC     is_current
# MAGIC )
# MAGIC VALUES (
# MAGIC     source.EncounterID,
# MAGIC     source.SRC_EncounterID,
# MAGIC     source.PatientID,
# MAGIC     TO_DATE(source.EncounterDate, 'M/d/yyyy'),
# MAGIC     source.EncounterType,
# MAGIC     source.ProviderID,
# MAGIC     source.DepartmentID,
# MAGIC     source.ProcedureCode,
# MAGIC     TO_TIMESTAMP(source.SRC_InsertedDate, 'M/d/yyyy'),
# MAGIC     TO_TIMESTAMP(source.SRC_ModifiedDate, 'M/d/yyyy'),
# MAGIC     source.Datasource,
# MAGIC     source.is_quarantined,
# MAGIC     current_timestamp(),
# MAGIC     current_timestamp(),
# MAGIC     true
# MAGIC );
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC select SRC_EncounterID,datasource,count(patientid) from  silver.encounters
# MAGIC group by all
# MAGIC order by 3 desc