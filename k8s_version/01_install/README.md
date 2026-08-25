# 01_install — Airflow on AKS + Azure Entra ID SSO + Azure Blob Remote Logging

This module deploys Airflow on an existing AKS cluster with Helm, enables Azure Entra ID (OIDC/OAuth) Single Sign-On, and configures **persistent remote task logging via Azure Blob Storage**.

---

## Prerequisites

- Existing AKS cluster and working `kubectl` context
- Helm v3
- Azure Entra ID app registration for Airflow UI login
- Azure Storage Account (`airflowworkshoplogs`) with a Blob Container named `airflow-logs`

---

## 1) Create Namespace & Secrets

### A) Create Namespace
```bash
kubectl apply -f manifests/namespace.yaml
```

### B) Create Azure Entra ID Auth Secret
```bash
kubectl -n airflow create secret generic airflow-entra-auth \
  --from-literal=AZURE_TENANT_ID='<tenant-id>' \
  --from-literal=AZURE_CLIENT_ID='<client-id>' \
  --from-literal=AZURE_CLIENT_SECRET='<client-secret>'
```

### C) Create Azure Blob Remote Logging Secret

#### Option A: Storage Account Access Key (Recommended & Most Reliable)
Copy **Key 1** from Azure Portal $\rightarrow$ Storage account `airflowworkshoplogs` $\rightarrow$ **Access keys**:

```bash
kubectl -n airflow create secret generic airflow-azure-storage \
  --from-literal=AIRFLOW_CONN_WASB_DEFAULT='{"conn_type": "wasb", "login": "airflowworkshoplogs", "password": "<YOUR_STORAGE_ACCOUNT_KEY>"}'
```

#### Option B: Account-Level SAS Token (JSON Format)
```bash
kubectl -n airflow create secret generic airflow-azure-storage \
  --from-literal=AIRFLOW_CONN_WASB_DEFAULT='{"conn_type": "wasb", "login": "airflowworkshoplogs", "extra": {"sas_token": "<YOUR_SAS_TOKEN>"}}'
```

> **Note:** Always use Airflow's **JSON connection format** so special characters (`&`, `=`, `%`) are preserved without URL-encoding corruption.

---

## 2) Add Helm Repo and Deploy Airflow

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f values-airflow.yaml
```

---

## 3) Validate Pods & LoadBalancer Access

```bash
kubectl get pods -n airflow
kubectl get svc -n airflow
```

**Expected:**
- `airflow-webserver` service type is `LoadBalancer`.
- `EXTERNAL-IP` is assigned for workshop access.

---

## 4) Azure Entra ID Redirect URI

Configure your Entra app redirect URI to:

```text
http://<loadbalancer-external-ip>:8080/oauth-authorized
```

---

## 5) Cloud-Native Architecture & Remote Logging Highlights

- **Dynamic Task Logging with Zero Pod Locking:** When task worker pods spawn and complete under `KubernetesExecutor`, they stream logs directly into Azure Blob Storage (`airflow-logs` container).
- **Persistent UI Log View:** The Airflow Webserver fetches task logs directly from Azure Blob Storage via `wasb_default`, allowing debugging even after the ephemeral worker pod has been deleted by Kubernetes.
- **No Shared RWX Volumes Needed:** Bypasses Kubernetes `ReadWriteMany` PVC limitations and IOPS throttling on Azure Files.
