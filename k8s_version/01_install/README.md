# 01_install — Airflow on AKS + Azure Entra ID SSO

This module deploys Airflow on an existing AKS cluster with Helm and enables Azure Entra ID (OIDC/OAuth) login for the Airflow UI.

## Prerequisites

- Existing AKS cluster and working `kubectl` context
- Helm v3
- Azure Entra app registration for Airflow UI login

## 1) Create namespace + secrets

```bash
kubectl apply -f manifests/namespace.yaml

kubectl -n airflow create secret generic airflow-entra-auth \
  --from-literal=AZURE_TENANT_ID='<tenant-id>' \
  --from-literal=AZURE_CLIENT_ID='<client-id>' \
  --from-literal=AZURE_CLIENT_SECRET='<client-secret>'
```

## 2) Add Helm repo and deploy Airflow

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f values-airflow.yaml
```

Notes:
- This module is pinned to Airflow image/version `2.11.0` in `values-airflow.yaml`.
- `extraEnv` is intentionally defined as a templated block (`extraEnv: |`) to satisfy chart schema validation while still using Secret `valueFrom` refs.

## 3) Validate pods + LoadBalancer access

```bash
kubectl get pods -n airflow
kubectl get svc -n airflow
```

Expected:
- `airflow-webserver` service type is `LoadBalancer`.
- `EXTERNAL-IP` is assigned (workshop access path).

## 4) Azure Entra ID redirect URI

Configure your Entra app redirect URI to:

```text
http://localhost:8080/oauth-authorized
```

Examples:
- `http://<loadbalancer-external-ip>:8080/oauth-authorized`

This follows the official FAB SSO guide for Airflow provider auth manager.

## 5) Airflow connection for ETL DB

After Module 02 DB is deployed, set connection env via Helm values (already included):

- `AIRFLOW_CONN_IOT_DB_CONN=postgresql://iot_user:***@iot-telemetry-db.airflow.svc.cluster.local:5432/iot_telemetry`

If you change service name/namespace, update this URI.

## 6) Working fixes already reflected in `values-airflow.yaml`

Based on live troubleshooting results, this module now includes:
- `defaultAirflowTag` and `airflowVersion` bumped to `2.11.0`.
- `logs.persistence.enabled: false` (avoids RWX/RWO storage conflict in workshop AKS setups).
- `webserver.service.type: LoadBalancer` (quick workshop reachability path).
- OIDC auto-discovery via `server_metadata_url` for Entra provider config.
- `AUTH_ROLES_SYNC_AT_LOGIN = False` to avoid login-time role sync issues observed in the workshop path.
- Ensure Entra app token configuration includes email claim for FAB user identity mapping.
