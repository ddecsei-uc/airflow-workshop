# 03_git_based_dag_retrieval — Git-Sync DAG Delivery on AKS

This module enables automatic DAG sync into Airflow pods using Helm `dags.gitSync`.

## What changed (current state)

- DAGs from previous Module 02/04 flow were consolidated here.
- This folder is now the single DAG source for the k8s workshop.

Current DAG files:
- `dags/minimal_etl.py` (`iot_telemetry_etl`)
- `dags/manual_sensor_cleaning_dag.py` (`manual_sensor_maintenance_classifier`)

## Deploy / upgrade with git-sync overlay

```bash
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f 01_install/values-airflow.yaml \
  -f 03_git_based_dag_retrieval/values-git-sync.yaml
```

## Critical setting (successful fix)

In `values-git-sync.yaml`, keep:

```yaml
subPath: "k8s_version/03_git_based_dag_retrieval/dags"
```

This is relative to repository root. Wrong `subPath` results in empty `/opt/airflow/dags` and no visible DAGs.

## Verify

```bash
kubectl logs -n airflow deploy/airflow-scheduler -c git-sync --tail=100
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- ls -la /opt/airflow/dags
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list-import-errors
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list
```

Expected:
- git-sync logs show normal sync cycles
- `/opt/airflow/dags` contains both DAG files
- `airflow dags list` includes both DAG IDs
