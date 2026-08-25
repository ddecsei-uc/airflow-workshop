# Apache Airflow Workshop (AKS / Kubernetes Version)

This directory provides the **Kubernetes (AKS) cloud-native deployment** of the Apache Airflow workshop.
It maintains the same learning structure and IoT ETL logic, while taking advantage of Helm, git-sync sidecars, and Azure Entra ID (OIDC) Single Sign-On.

> **Scope:** The AKS cluster is assumed to already exist.

---

## 📂 Structure

- **[`01_install/`](file:///C:/Users/David/Downloads/homeLab/airflow/k8s_version/01_install/README.md)** — Airflow on AKS via Helm Chart + Azure Entra ID SSO configuration
- **[`02_usecase_etl/`](file:///C:/Users/David/Downloads/homeLab/airflow/k8s_version/02_usecase_etl/README.md)** — IoT Telemetry DB, Flask API, and real-time Before vs. After Dashboard
- **[`03_git_based_dag_retrieval/`](file:///C:/Users/David/Downloads/homeLab/airflow/k8s_version/03_git_based_dag_retrieval/README.md)** — Git-based automatic DAG synchronization (`git-sync`), containing all workshop DAGs:
  - `minimal_etl.py` (`iot_telemetry_etl`)
  - `manual_sensor_cleaning_dag.py` (`manual_sensor_maintenance_classifier`)
- **[`walkthrough.md`](file:///C:/Users/David/Downloads/homeLab/airflow/k8s_version/walkthrough.md)** — Master execution log, DAG pod paths, Azure Entra ID dynamic RBAC deep dive, and troubleshooting guide

---

## 🚀 Quick Start (High-Level Flow)

1. **Set Kubernetes Context:** Ensure `kubectl` is pointed to your AKS cluster.
2. **Deploy Airflow with Helm (Module 01):**
   ```bash
   kubectl apply -f 01_install/manifests/namespace.yaml
   # Create Entra secret & deploy Helm chart
   helm upgrade --install airflow apache-airflow/airflow -n airflow -f 01_install/values-airflow.yaml
   ```
3. **Deploy IoT Database, API & Dashboard (Module 02):**
   ```bash
   kubectl apply -n airflow -f 02_usecase_etl/k8s/
   ```
4. **Enable Git-Sync DAG Retrieval (Module 03):**
   ```bash
   helm upgrade --install airflow apache-airflow/airflow \
     -n airflow \
     -f 01_install/values-airflow.yaml \
     -f 03_git_based_dag_retrieval/values-git-sync.yaml
   ```
5. **Run the Live Workshop Demo:**
   - Port-forward Dashboard & API:
     ```bash
     kubectl port-forward -n airflow svc/airflow-dashboard 8081:80
     kubectl port-forward -n airflow svc/iot-api 5000:5000
     ```
   - Open Dashboard: `http://localhost:8081/?api=http://localhost:5000`
   - Trigger DAGs in Airflow UI (`http://<webserver-loadbalancer-ip>:8080`) and observe real-time transformations!
