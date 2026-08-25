# 01_install — Airflow on AKS + Azure Entra SSO

This module deploys Airflow to an existing AKS cluster and enables Azure Entra SSO for Airflow UI login.

## Prerequisites

- Existing AKS cluster and working `kubectl` context
- Helm v3
- Azure Entra app registration for Airflow UI login

## 1) Create namespace + Entra secret

```bash
kubectl apply -f manifests/namespace.yaml

kubectl -n airflow create secret generic airflow-entra-auth \
  --from-literal=AZURE_TENANT_ID='<tenant-id>' \
  --from-literal=AZURE_CLIENT_ID='<client-id>' \
  --from-literal=AZURE_CLIENT_SECRET='<client-secret>'
```

## 2) Deploy Airflow

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f values-airflow.yaml
```

## 3) Verify deployment

```bash
kubectl get pods -n airflow
kubectl get svc -n airflow
```

Expected:
- `airflow-webserver` service type is `LoadBalancer`
- `EXTERNAL-IP` is assigned

## 4) Entra redirect URI

Configure your Entra app redirect URI to:

```text
http://<airflow-webserver-loadbalancer-ip>:8080/oauth-authorized
```

## 5) How SSO roles work in current workshop setup

Current working behavior from `values-airflow.yaml`:

- `AUTH_TYPE = AUTH_OAUTH`
- `AUTH_USER_REGISTRATION = True`
- `AUTH_USER_REGISTRATION_ROLE = "Admin"`
- `AUTH_ROLES_SYNC_AT_LOGIN = False`

Meaning:
- Authenticated Entra users are auto-created in Airflow
- They receive `Admin` role by default
- Roles are **not dynamically remapped on each login** in this workshop profile

(If needed later, dynamic mapping can be enabled with `AUTH_ROLES_SYNC_AT_LOGIN = True` + `AUTH_ROLES_MAPPING`.)
