# 02_usecase_etl — IoT ETL on AKS

Deploy PostgreSQL telemetry DB, Flask API, and live dashboard into AKS.

---

## 1) Images

Current manifests use prebuilt container images:
- API: `cheesecakeslice/airflow-workshop:v1.0`
- Dashboard: `cheesecakeslice/airflow-dashboard:latest`

If you want to build and push your own container images:
```bash
# API image
docker build -t <registry>/iot-api:latest ./api
docker push <registry>/iot-api:latest

# Dashboard image
docker build -t <registry>/airflow-dashboard:latest ./dashboard
docker push <registry>/airflow-dashboard:latest
```

---

## 2) Apply Kubernetes Manifests

Apply the PostgreSQL database, API backend, and dashboard into the `airflow` namespace:

```bash
kubectl apply -n airflow -f k8s/postgres-configmap.yaml
kubectl apply -n airflow -f k8s/postgres-statefulset.yaml
kubectl apply -n airflow -f k8s/postgres-service.yaml

kubectl apply -n airflow -f k8s/iot-api-deployment.yaml
kubectl apply -n airflow -f k8s/iot-api-service.yaml

kubectl apply -n airflow -f k8s/dashboard-deployment.yaml
kubectl apply -n airflow -f k8s/dashboard-service.yaml
```

*(Optional: `kubectl apply -n airflow -f k8s/ingress.yaml` if you explicitly configured ingress).*

---

## 3) Workshop Demo Access (Port-Forward, Recommended)

For maximum reliability during workshops, access the dashboard and API via `kubectl port-forward`:

In two separate terminals:
```bash
kubectl port-forward -n airflow svc/airflow-dashboard 8081:80
kubectl port-forward -n airflow svc/iot-api 5000:5000
```

Open the dashboard with the explicit API override parameter:
👉 **`http://localhost:8081/?api=http://localhost:5000`**

---

## 4) DAG Deployment (Via Module 03 Git-Sync)

Both DAGs (`iot_telemetry_etl` and `manual_sensor_maintenance_classifier`) reside in **`03_git_based_dag_retrieval/dags/`**.

When Module 03 is applied via Helm overlay (`values-git-sync.yaml`), `git-sync` automatically delivers these DAGs into `/opt/airflow/dags` across all Airflow pods.

*(For quick local testing without git-sync, you can copy directly to the scheduler:)*
```bash
SCHED=$(kubectl get pod -n airflow -l component=scheduler -o jsonpath='{.items[0].metadata.name}')
kubectl cp ../03_git_based_dag_retrieval/dags/minimal_etl.py airflow/$SCHED:/opt/airflow/dags/minimal_etl.py
kubectl cp ../03_git_based_dag_retrieval/dags/manual_sensor_cleaning_dag.py airflow/$SCHED:/opt/airflow/dags/manual_sensor_cleaning_dag.py
```

---

## 5) Verify Workloads & API Health

```bash
kubectl get pods -n airflow
kubectl get svc -n airflow
curl -sS http://localhost:5000/api/health
```

Expected output:
```json
{"status":"ok"}
```

---

## 6) Insert Live Sensor Data (`add_sensor_data.py`)

Port-forward PostgreSQL locally and run the data generator:

```bash
kubectl port-forward -n airflow svc/iot-telemetry-db 5433:5432
```

In a second terminal:
```bash
# Insert normal batch
python add_sensor_data.py

# Insert anomalous overheat readings (>75°C / >85°C)
python add_sensor_data.py --anomaly

# Reset database to initial seed state
python add_sensor_data.py --reset
```

---

## 7) Run the Live Showcase

1. Insert anomalous data: `python add_sensor_data.py --anomaly`
2. Open Dashboard: `http://localhost:8081/?api=http://localhost:5000` (shows raw un-processed readings with `✗ no`).
3. Trigger DAG `iot_telemetry_etl` in Airflow UI → Metrics & Alerts panels populate live, raw rows turn to `✓ yes`.
4. Trigger DAG `manual_sensor_maintenance_classifier` in Airflow UI → Maintenance Queue panel populates with prioritized tickets.
