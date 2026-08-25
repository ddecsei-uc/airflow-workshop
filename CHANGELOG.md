# Changelog

All notable changes to the Apache Airflow Workshop repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.2.0] - 2026-08-25

### Added
- **Consolidated AKS DAG Suite**: Moved all workshop DAGs (`minimal_etl.py` and `manual_sensor_cleaning_dag.py`) into `k8s_version/03_git_based_dag_retrieval/dags/` for unified Git-Sync orchestration.
- **Git-Sync SubPath Configuration**: Added `subPath: "airflow/k8s_version/03_git_based_dag_retrieval/dags"` and sync polling interval (`wait: 30`) to `k8s_version/03_git_based_dag_retrieval/values-git-sync.yaml` so Airflow scheduler correctly parses DAGs within repository subdirectories.
- **Pod DAG Location Deep Dive**: Added technical documentation to `k8s_version/walkthrough.md` explaining `/opt/airflow/dags` filesystem path, shared `emptyDir` volume mounting, and scheduler database serialization (`serialized_dag`).
- **Azure Entra ID Dynamic RBAC Guide**: Added OIDC token exchange sequence diagrams and configuration reference (`AUTH_ROLES_SYNC_AT_LOGIN = True` + `AUTH_ROLES_MAPPING` with Azure App Roles / Security Groups) in `k8s_version/walkthrough.md`.
- **Module 03 Diagnostic Playbook**: Added CLI commands for git-sync log inspection, `/opt/airflow/dags` directory verification, DAG import error checking, and DAG list validation.

### Changed
- **Streamlined AKS Architecture**: Refactored `k8s_version` workflow to a focused sequential 3-module path:
  - `01_install`: Airflow on AKS via Helm + Azure Entra ID SSO
  - `02_usecase_etl`: IoT Telemetry Database + Flask API + Real-time Dashboard
  - `03_git_based_dag_retrieval`: Cloud-native Git-Sync automated DAG deployment
- Renamed `k8s_version/05_git_based_dag_retrieval` to `k8s_version/03_git_based_dag_retrieval` to match the exact module count and progression in the Kubernetes track.
- Updated `k8s_version/README.md`, `k8s_version/01_install/README.md`, `k8s_version/02_usecase_etl/README.md`, `k8s_version/03_git_based_dag_retrieval/README.md`, and `k8s_version/walkthrough.md`.

### Removed
- Removed redundant Kubernetes modules (`k8s_version/03_operational_painpoints`, `k8s_version/04_manual_dag_exercise`, and `k8s_version/06_monitoring_airflow`) to eliminate duplication and keep the AKS track cloud-native.

---

## [1.1.0] - 2026-08-19

### Added
- **Prebuilt Container Images**: Integrated `cheesecakeslice/airflow-workshop:v1.0` (API) and `cheesecakeslice/airflow-dashboard:latest` (Dashboard) in Kubernetes manifests.
- **Dynamic API Override**: Added `?api=http://...` URL query parameter support to the web dashboard for zero-friction `kubectl port-forward` demo access.

### Changed
- **Airflow 2.11.0 Helm Baseline**: Pinned `defaultAirflowTag` and `airflowVersion` to `2.11.0` in `k8s_version/01_install/values-airflow.yaml`.
- **OIDC Discovery & Service Reachability**: Configured `server_metadata_url` for Azure Entra ID tenant discovery, `webserver.service.type: LoadBalancer`, and disabled `logs.persistence` to prevent storage class conflicts.
- **Database Connection String**: Corrected `AIRFLOW_CONN_IOT_DB_CONN` service DNS URI for internal cluster communication.

---

## [1.0.0] - 2026-08-18

### Added
- **Module 07 (Datasets & Data-Aware Scheduling)**: Added `07_datasets_orchestration` featuring `dataset_producer_local.py` and `dataset_consumer_local.py` using Airflow `Dataset` URIs.
- **Module 06 (Observability & Monitoring)**: Added `06_monitoring_airflow` with Prometheus scraping configuration, StatsD exporter integration, and pre-built Grafana dashboards (`airflow-workshop-overview.json`).
- **Git-Sync Configuration Templates**: Added `.airflowignore.example`, `.env.git-sync.example`, and `docker-compose.git-sync.yaml` in `05_git_based_dag_retrieval`.

### Changed
- Verified full local Docker Compose workshop stack on bare-metal / VM environments.
- Standardized cross-module file path references and presenter cheat sheets.

---

## [0.1.0] - 2026-08-17

### Added
- **Initial Workshop Release**:
  - `01_install`: Docker Compose and Helm installation manifests for Airflow cluster.
  - `02_usecase_etl`: IoT telemetry pipeline with PostgreSQL database (`raw_sensor_readings`, `daily_sensor_metrics`, `sensor_alerts`), TaskFlow API DAG (`minimal_etl.py`), Flask API, and real-time glassmorphism web dashboard.
  - `03_operational_painpoints`: Production incident management and troubleshooting playbooks.
  - `04_manual_dag_exercise`: Hands-on DAG deployment and device risk maintenance classifier (`manual_sensor_cleaning_dag.py`).
  - `05_git_based_dag_retrieval`: Automated DAG retrieval using `git-sync`.
  - `k8s_version`: Kubernetes / AKS cloud deployment track with Azure Entra ID SSO integration.
- **Repository Hygiene & Open Source Standards**:
  - Added `.gitignore`, `LICENSE` (MIT), `CONTRIBUTING.md`, `SECURITY.md`, and sanitized documentation placeholders.
