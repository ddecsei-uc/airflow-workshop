# Apache Airflow Workshop (AKS / Kubernetes Version)

This folder contains the AKS workshop track in its current **working** form:
- local review flow
- port-forwarded API/dashboard access
- domainless workshop path
- Azure Entra SSO enabled for Airflow UI

## Structure

- `01_install/` — Deploy Airflow on AKS via Helm + configure Azure Entra SSO
- `02_usecase_etl/` — Deploy IoT DB + API + dashboard and run the ETL demo
- `03_git_based_dag_retrieval/` — Git-sync DAG delivery (contains all workshop DAGs)
- `walkthrough.md` — End-to-end runbook + verification commands

## DAG ownership (current)

All workshop DAGs are now in:

- `03_git_based_dag_retrieval/dags/minimal_etl.py` (`iot_telemetry_etl`)
- `03_git_based_dag_retrieval/dags/manual_sensor_cleaning_dag.py` (`manual_sensor_maintenance_classifier`)

No separate manual DAG module is required.

## High-level flow

1. Deploy Airflow + Entra SSO (`01_install`).
2. Deploy ETL app stack (`02_usecase_etl`).
3. Start local port-forwards:
   - dashboard: `kubectl port-forward -n airflow svc/airflow-dashboard 8081:80`
   - API: `kubectl port-forward -n airflow svc/iot-api 5000:5000`
4. Open dashboard:
   - `http://localhost:8081/?api=http://localhost:5000`
5. Enable git-sync (`03_git_based_dag_retrieval`) so DAGs are auto-delivered to Airflow.
6. Trigger DAGs in Airflow UI and validate dashboard updates.
