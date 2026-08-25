from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

POSTGRES_CONN_ID = "iot_db_conn"
TEMP_THRESHOLD = 75.0


@dag(
    dag_id="iot_telemetry_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=1)},
    tags=["workshop", "iot", "etl", "aks"],
)
def iot_telemetry_etl():
    @task
    def extract():
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        rows = hook.get_records(
            """
            SELECT reading_id, device_id, location, temperature_celsius, humidity_pct, battery_pct, reading_timestamp
            FROM raw_sensor_readings
            WHERE processed = FALSE
            """
        )
        return [
            {
                "reading_id": r[0],
                "device_id": r[1],
                "location": r[2],
                "temperature_celsius": float(r[3]),
                "humidity_pct": float(r[4]),
                "battery_pct": float(r[5]),
                "reading_timestamp": r[6],
            }
            for r in rows
        ]

    @task
    def transform(records):
        if not records:
            return {"metrics": [], "alerts": [], "ids": []}

        buckets = {}
        alerts = []
        ids = []

        for rec in records:
            ids.append(rec["reading_id"])
            day = str(rec["reading_timestamp"])[:10]
            key = (rec["device_id"], rec["location"], day)
            buckets.setdefault(key, []).append(rec["temperature_celsius"])

            if rec["temperature_celsius"] > TEMP_THRESHOLD:
                alerts.append(
                    {
                        "reading_id": rec["reading_id"],
                        "device_id": rec["device_id"],
                        "alert_type": "HIGH_TEMPERATURE",
                        "metric_value": rec["temperature_celsius"],
                        "threshold_value": TEMP_THRESHOLD,
                        "severity": "CRITICAL" if rec["temperature_celsius"] >= 90 else "WARNING",
                    }
                )

        metrics = []
        for (device_id, location, day), temps in buckets.items():
            metrics.append(
                {
                    "device_id": device_id,
                    "location": location,
                    "metric_date": day,
                    "avg_temperature": round(sum(temps) / len(temps), 2),
                    "max_temperature": max(temps),
                    "min_temperature": min(temps),
                    "total_readings": len(temps),
                }
            )

        return {"metrics": metrics, "alerts": alerts, "ids": ids}

    @task
    def load(payload):
        if not payload["ids"]:
            return "No new rows"

        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = hook.get_conn()
        cur = conn.cursor()
        try:
            for m in payload["metrics"]:
                cur.execute(
                    """
                    INSERT INTO daily_sensor_metrics(device_id, location, metric_date, avg_temperature, max_temperature, min_temperature, total_readings)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (device_id, metric_date) DO UPDATE SET
                      avg_temperature=EXCLUDED.avg_temperature,
                      max_temperature=GREATEST(daily_sensor_metrics.max_temperature, EXCLUDED.max_temperature),
                      min_temperature=LEAST(daily_sensor_metrics.min_temperature, EXCLUDED.min_temperature),
                      total_readings=daily_sensor_metrics.total_readings + EXCLUDED.total_readings,
                      calculated_at=NOW();
                    """,
                    (
                        m["device_id"],
                        m["location"],
                        m["metric_date"],
                        m["avg_temperature"],
                        m["max_temperature"],
                        m["min_temperature"],
                        m["total_readings"],
                    ),
                )

            for a in payload["alerts"]:
                cur.execute(
                    """
                    INSERT INTO sensor_alerts(reading_id, device_id, alert_type, metric_value, threshold_value, severity)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        a["reading_id"],
                        a["device_id"],
                        a["alert_type"],
                        a["metric_value"],
                        a["threshold_value"],
                        a["severity"],
                    ),
                )

            cur.execute(
                "UPDATE raw_sensor_readings SET processed = TRUE WHERE reading_id = ANY(%s)",
                (payload["ids"],),
            )
            conn.commit()
            return f"processed={len(payload['ids'])}"
        finally:
            cur.close()
            conn.close()

    load(transform(extract()))


iot_telemetry_etl()
