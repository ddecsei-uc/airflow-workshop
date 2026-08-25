# 03_git_based_dag_retrieval — Git-Based DAG Retrieval on AKS (git-sync)

This module configures **automatic DAG synchronization** into Airflow pods running on AKS using the native `git-sync` sidecar pattern from the official Apache Airflow Helm chart.

---

## 🎯 What This Module Contains

All DAGs for the AKS workshop are maintained inside `03_git_based_dag_retrieval/dags/`:
1. **`minimal_etl.py`** (`iot_telemetry_etl`): The hourly TaskFlow ETL pipeline processing sensor readings, computing aggregations into `daily_sensor_metrics`, and flagging >75°C threshold violations into `sensor_alerts`.
2. **`manual_sensor_cleaning_dag.py`** (`manual_sensor_maintenance_classifier`): The on-demand maintenance classification pipeline scoring device temperatures and dispatching action tickets into `sensor_maintenance_queue`.

---

## ⚙️ How Git-Sync Works

```text
[ Developer / Git Repo ]
           │
           ▼ (git push)
[ GitHub / Remote Repo: https://github.com/DecseiD/airflow-workshop.git ]
           │
           ▼ (polls every 30s)
[ git-sync sidecar container in scheduler/webserver pods ]
           │ (clones & symlinks subPath into shared volume)
           ▼
[ Pod filesystem: /opt/airflow/dags ]
           │ (Airflow scheduler scans and parses .py files)
           ▼
[ Airflow Metadata DB (serialized_dag) ]
           │ (Webserver and CLI read from metadata DB)
           ▼
[ Airflow Web UI & CLI: DAGs visible and executable ]
```

---

## 🚀 Deployment Instructions

### Step 1: Deploy / Upgrade Airflow with Git-Sync Overlay

Run Helm upgrade applying the base values and the git-sync overlay:

```bash
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f 01_install/values-airflow.yaml \
  -f 03_git_based_dag_retrieval/values-git-sync.yaml
```

*(If running from within `03_git_based_dag_retrieval/`, use `-f ../01_install/values-airflow.yaml -f values-git-sync.yaml`)*

---

## 🔍 Verification & Diagnostics

### 1. Check git-sync sidecar logs
Verify that the `git-sync` container successfully cloned the repository:

```bash
kubectl logs -n airflow deploy/airflow-scheduler -c git-sync --tail=50
```

**Expected output:**
```text
level=info msg="syncing git" branch="main" rev="HEAD" ...
level=info msg="update local" rev="<commit-hash>" ...
level=info msg="sync complete" ...
```

### 2. Inspect the `/opt/airflow/dags` directory inside the scheduler pod
Confirm that the DAG files exist inside the pod's DAGs folder:

```bash
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- ls -la /opt/airflow/dags
```

**Expected output:**
```text
manual_sensor_cleaning_dag.py
minimal_etl.py
```

### 3. Check for Airflow DAG import errors
If files exist in `/opt/airflow/dags` but do not appear in the UI or CLI:

```bash
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list-import-errors
```

### 4. List parsed DAGs via Airflow CLI
```bash
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list
```

**Expected output:**
```text
dag_id                               | filepath                      | owner   | paused
=====================================+===============================+=========+=======
iot_telemetry_etl                    | /opt/airflow/dags/minimal_... | airflow | False 
manual_sensor_maintenance_classifier | /opt/airflow/dags/manual_...  | airflow | True  
```

---

## 🛠️ Why Were DAGs Missing? (Root Cause & Fix)

If you deployed Module 03 and no DAGs appeared in the UI or CLI, the most common causes and fixes are:

### Root Cause 1: Missing or Incorrect `subPath` in Helm Values (Most Common)
- **Problem:** In https://github.com/DecseiD/airflow-workshop.git, the repository root contains `k8s_version/` directly. If `subPath` is empty (`""`) or incorrectly includes repo prefixes (e.g. `airflow/` or `airflow-workshop/`), Airflow looks for non-existent folders and mounts an empty directory at `/opt/airflow/dags`.
- **Fix:** In `values-git-sync.yaml`, configure `subPath` exactly relative to the repo root:
  ```yaml
  subPath: "k8s_version/03_git_based_dag_retrieval/dags"
  ```

### Root Cause 2: Git-Sync Clone Authentication / Network Failure
- **Problem:** The `git-sync` sidecar is failing to pull from the remote repository (e.g. private repo without SSH secret, wrong branch name, rate limit).
- **Diagnosis:** Run `kubectl logs -n airflow deploy/airflow-scheduler -c git-sync`.
- **Fix:** Check repo URL, branch (`main`), and configure `sshKeySecret` if using a private repository.

### Root Cause 3: Scheduler DAG Parsing Delay
- **Problem:** Git-sync pulls files on an interval (`wait: 30`), and Airflow scheduler scans the folder periodically (`min_file_process_interval: 30`).
- **Fix:** Wait 30-60 seconds after pod readiness, or trigger a manual scan by running `kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags reserialize`.
