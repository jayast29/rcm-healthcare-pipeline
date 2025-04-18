# Databricks notebook source
spark

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS city_hrcm_adb_ws.audit;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS city_hrcm_adb_ws.audit.load_logs (
# MAGIC     id BIGINT GENERATED ALWAYS AS IDENTITY,
# MAGIC     data_source STRING,
# MAGIC     tablename STRING,
# MAGIC     numberofrowscopied INT,
# MAGIC     watermarkcolumnname STRING,
# MAGIC     loaddate TIMESTAMP
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC truncate table city_hrcm_adb_ws.audit.load_logs

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from city_hrcm_adb_ws.audit.load_logs

# COMMAND ----------

