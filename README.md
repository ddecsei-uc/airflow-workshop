# 🚀 Apache Airflow Workshop: From Raw Ingestion to Refined Intelligence

This repository is a **demo/tutorial workshop** for engineering peers.
It demonstrates an end-to-end Airflow workflow using local Docker services and a practical IoT telemetry ETL scenario.

> This repo is intentionally optimized for **quick local run**. It is not intended as a production distribution.

---

## 📍 Local Workshop Services

All workshop services run on your local lab host.

| Service | Access URL / Connection | Credentials | Role in Workshop |
| :--- | :--- | :--- | :--- |
| **Before vs After ETL Dashboard** | **[http://localhost:3001](http://localhost:3001)** | N/A | Main showcase for raw vs transformed data |
| **Apache Airflow Web UI** | **[http://localhost:8080](http://localhost:8080)** | `admin` / `admin` | DAG operations, task state transitions, and logs |
| **IoT Target Database** | **`localhost:5433`** | `iot_user` / `iot_password` | PostgreSQL target DB (`iot_telemetry`) |
| **Host Shell** | `ssh <user>@<HOST_IP>` (optional if remote host) | SSH key or local console | Presenter terminal for container and CLI commands |

---

## 🎙️ Phase-by-Phase Instructor Presentation Script (60 min)

### Phase 1: Infrastructure & Container Roles (Minutes 00–10)
- **Goal:** Explain Airflow core services in a containerized deployment.
- **Module Document:** [`01_install/README.md`](./01_install/README.md)
- **Talking Points:**
  1. Open Airflow UI at `http://localhost:8080`.
  2. Explain the 4 core components:
     - **Webserver**: UI application.
     - **Scheduler**: parses DAGs and dispatches tasks.
     - **Triggerer**: async loop for deferred tasks.
     - **Postgres**: metadata database.
  3. Highlight memory limits configured in compose for host safety.

### Phase 2: TaskFlow API & Pipeline Execution (Minutes 10–30)
- **Goal:** Walk through modern Airflow DAG design.
- **Module Document:** [`02_usecase_etl/README.md`](./02_usecase_etl/README.md)
- **Code File:** [`02_usecase_etl/dags/minimal_etl.py`](./02_usecase_etl/dags/minimal_etl.py)
- **Talking Points:**
  1. `@dag` and `@task` usage.
  2. **Extract:** read unprocessed rows from `raw_sensor_readings`.
  3. **Transform:** compute metrics + threshold anomalies (>75°C).
  4. **Load:** upsert into `daily_sensor_metrics`, insert `sensor_alerts`, mark processed rows.
  5. Trigger `iot_telemetry_etl` and inspect logs.

### Phase 3: Before/After ETL Outcome (Minutes 30–45)
- **Goal:** Visually prove ETL business value.
- **Module Document:** [`02_usecase_etl/dashboard/index.html`](./02_usecase_etl/dashboard/index.html)
- **Live Demo URL:** **[http://localhost:3001](http://localhost:3001)**
- **Talking Points:**
  1. Show raw/unprocessed telemetry first.
  2. Trigger `iot_telemetry_etl`, then refresh dashboard.
  3. Show metrics, chart, alerts, and maintenance queue updates.
  4. If API is unreachable, verify `http://localhost:5000/api/health` (or use `?api=http://<HOST_IP>:5000`).

### Phase 4: Manual DAG Exercise (Minutes 45–60)
- **Goal:** Show live DAG onboarding and immediate business impact.
- **Module Document:** [`04_manual_dag_exercise/README.md`](./04_manual_dag_exercise/README.md)
- **Talking Points:**
  1. Copy new DAG into `01_install/dags/`.
  2. Enable + trigger DAG in Airflow UI.
  3. Show maintenance queue before/after in PostgreSQL.

### Phase 5: Git-Based DAG Retrieval (Minutes 60–72, optional extension)
- **Goal:** Showcase production-like developer flow for DAG delivery.
- **Module Document:** [`05_git_based_dag_retrieval/README.md`](./05_git_based_dag_retrieval/README.md)
- **Talking Points:**
  1. DAGs are retrieved from Git through a sync mechanism rather than manual copy.
  2. Developer flow: commit/push -> sync interval -> scheduler parse -> DAG appears.
  3. Triage path: auth failures, wrong branch/subpath, DAG import errors.

### Phase 6: Dataset-Driven Orchestration (Minutes 72–80, optional extension)
- **Goal:** Demonstrate Airflow Dataset scheduling in the UI.
- **Module Document:** [`07_datasets_orchestration/README.md`](./07_datasets_orchestration/README.md)
- **Talking Points:**
  1. Trigger producer DAG and emit dataset event.
  2. Confirm dataset update in **Datasets** UI.
  3. Show consumer DAG auto-triggered by dataset.

### Phase 7: Monitoring Airflow (Minutes 80–88, optional extension)
- **Goal:** Demonstrate lightweight observability with Prometheus + Grafana.
- **Module Document:** [`06_monitoring_airflow/README.md`](./06_monitoring_airflow/README.md)
- **Talking Points:**
  1. Airflow emits metrics via StatsD exporter.
  2. Prometheus scrapes metrics and Grafana visualizes scheduler/task behavior.
  3. Workshop focus: practical visibility and triage, not full SRE platform complexity.

### Phase 8: Operational Pain Points (Minutes 88–95, capstone)
- **Goal:** End with structured troubleshooting and production failure modes.
- **Module Document:** [`03_operational_painpoints/troubleshooting_guide.md`](./03_operational_painpoints/troubleshooting_guide.md)
- **Talking Points:**
  1. Missing DAGs / import errors.
  2. Scheduler heartbeat issues and queued-task stalls.
  3. Webserver scaling and timeout behavior.
  4. Security/log-isolation concerns in shared environments.
  5. Single-node resource hygiene (memory, logs, disk pressure).

---

## 🛠️ Presenter Command Cheat Sheet

```bash
# Enter project
cd airflow-workshop

# Start Module 01 Airflow core stack
cd 01_install
docker compose up airflow-init
docker compose up -d

# Start Module 02 DB/API/dashboard
cd ../02_usecase_etl
docker compose -f docker-compose-db.yaml up -d --build

# Trigger ETL DAG
cd ../01_install
docker compose exec airflow-webserver airflow dags trigger iot_telemetry_etl

# Validate API health
curl http://localhost:5000/api/health

# Optional Module 07 dataset demo (Module 05 git-sync already provides DAG files)
docker compose exec airflow-webserver airflow dags trigger dataset_arrival_producer_local

# Optional Module 06 monitoring stack
cd ../01_install
docker compose -f docker-compose.yaml -f ../06_monitoring_airflow/docker-compose.monitoring.yaml up -d
```
