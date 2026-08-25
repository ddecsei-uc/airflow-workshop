# 02_usecase_etl — IoT ETL on AKS

Deploy PostgreSQL telemetry DB, Flask API, and dashboard.

## 1) Apply manifests

```bash
kubectl apply -n airflow -f k8s/postgres-configmap.yaml
kubectl apply -n airflow -f k8s/postgres-statefulset.yaml
kubectl apply -n airflow -f k8s/postgres-service.yaml

kubectl apply -n airflow -f k8s/iot-api-deployment.yaml
kubectl apply -n airflow -f k8s/iot-api-service.yaml

kubectl apply -n airflow -f k8s/dashboard-deployment.yaml
kubectl apply -n airflow -f k8s/dashboard-service.yaml
```

Optional only (not required for workshop flow):

```bash
kubectl apply -n airflow -f k8s/ingress.yaml
```

## 2) Workshop access (port-forward)

In separate terminals:

```bash
kubectl port-forward -n airflow svc/airflow-dashboard 8081:80
kubectl port-forward -n airflow svc/iot-api 5000:5000
```

Open dashboard with explicit API override:

```text
http://localhost:8081/?api=http://localhost:5000
```

## 3) Verify API

```bash
curl -sS http://localhost:5000/api/health
```

Expected:

```json
{"status":"ok"}
```

## 4) DAG source of truth

DAGs are delivered by Module 03 git-sync from:

- `03_git_based_dag_retrieval/dags/minimal_etl.py`
- `03_git_based_dag_retrieval/dags/manual_sensor_cleaning_dag.py`

No manual DAG copy step is required in the normal workshop path.

## 5) Insert sample data

```bash
kubectl port-forward -n airflow svc/iot-telemetry-db 5433:5432
python add_sensor_data.py --anomaly
```

## 6) Run demo flow

1. Trigger DAG `iot_telemetry_etl` in Airflow UI
2. Open dashboard: `http://localhost:8081/?api=http://localhost:5000`
3. Confirm metrics/alerts update
4. Trigger `manual_sensor_maintenance_classifier`
5. Confirm maintenance queue data appears

## 7) Known working fix for `API unavailable`

Dashboard JS defaults API to `${window.location.hostname}:5000`.
In workshop mode, always open dashboard with explicit API override:

- `http://localhost:8081/?api=http://localhost:5000`
