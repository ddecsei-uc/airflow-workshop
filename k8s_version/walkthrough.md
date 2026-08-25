# Walkthrough (AKS) — Current Working Workshop Path

## 1) Context + namespace

```bash
kubectl config current-context
kubectl get ns airflow
```

## 2) Deploy Airflow + SSO (Module 01)

```bash
kubectl apply -f 01_install/manifests/namespace.yaml

kubectl -n airflow create secret generic airflow-entra-auth \
  --from-literal=AZURE_TENANT_ID='<tenant-id>' \
  --from-literal=AZURE_CLIENT_ID='<client-id>' \
  --from-literal=AZURE_CLIENT_SECRET='<client-secret>'

helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f 01_install/values-airflow.yaml
```

Verify:

```bash
kubectl get pods -n airflow
kubectl get svc -n airflow
```

Open Airflow at:
- `http://<airflow-webserver-loadbalancer-ip>:8080`

SSO callback check:
- `/oauth-authorized`

## 3) Deploy ETL stack (Module 02)

```bash
kubectl apply -n airflow -f 02_usecase_etl/k8s/postgres-configmap.yaml
kubectl apply -n airflow -f 02_usecase_etl/k8s/postgres-statefulset.yaml
kubectl apply -n airflow -f 02_usecase_etl/k8s/postgres-service.yaml
kubectl apply -n airflow -f 02_usecase_etl/k8s/iot-api-deployment.yaml
kubectl apply -n airflow -f 02_usecase_etl/k8s/iot-api-service.yaml
kubectl apply -n airflow -f 02_usecase_etl/k8s/dashboard-deployment.yaml
kubectl apply -n airflow -f 02_usecase_etl/k8s/dashboard-service.yaml
```

## 4) Start workshop port-forwards

Run in separate terminals:

```bash
kubectl port-forward -n airflow svc/airflow-dashboard 8081:80
kubectl port-forward -n airflow svc/iot-api 5000:5000
kubectl port-forward -n airflow svc/iot-telemetry-db 5433:5432
```

Checks:

```bash
curl -sS http://localhost:5000/api/health
```

Dashboard URL:
- `http://localhost:8081/?api=http://localhost:5000`

## 5) Enable DAG git-sync (Module 03)

```bash
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f 01_install/values-airflow.yaml \
  -f 03_git_based_dag_retrieval/values-git-sync.yaml
```

## 6) DAG visibility verification

```bash
kubectl logs -n airflow deploy/airflow-scheduler -c git-sync --tail=100
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- ls -la /opt/airflow/dags
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list-import-errors
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list
```

Expected DAGs:
- `iot_telemetry_etl`
- `manual_sensor_maintenance_classifier`

## 7) End-to-end run

1. Insert anomaly data:
   ```bash
   cd 02_usecase_etl
   python add_sensor_data.py --anomaly
   ```
2. Trigger `iot_telemetry_etl`
3. Trigger `manual_sensor_maintenance_classifier`
4. Validate dashboard + maintenance queue updates

---

## Deep dive A — Where Airflow reads DAGs

Airflow scheduler reads DAG files from:

```text
/opt/airflow/dags
```

Quick check:

```bash
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- ls -la /opt/airflow/dags
```

If this path is empty, DAGs will not appear in UI/CLI.

## Deep dive B — Entra SSO role behavior in this workshop

Current configured behavior (`01_install/values-airflow.yaml`):

- `AUTH_USER_REGISTRATION = True`
- `AUTH_USER_REGISTRATION_ROLE = "Admin"`
- `AUTH_ROLES_SYNC_AT_LOGIN = False`

Meaning:
- Entra-authenticated users are auto-created in Airflow
- They get `Admin` role by default
- Dynamic per-login role mapping is currently disabled

If you want dynamic mapping later, enable `AUTH_ROLES_SYNC_AT_LOGIN = True` and define `AUTH_ROLES_MAPPING`.
