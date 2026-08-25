from datetime import datetime

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

CONN_ID = "iot_db_conn"


@dag(
    dag_id="manual_sensor_maintenance_classifier",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["workshop", "maintenance", "aks"],
)
def manual_sensor_maintenance_classifier():
    @task
    def classify_and_insert():
        hook = PostgresHook(postgres_conn_id=CONN_ID)
        conn = hook.get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT device_id, location, MAX(temperature_celsius) AS current_temp
                FROM raw_sensor_readings
                GROUP BY device_id, location
                """
            )
            rows = cur.fetchall()

            for device_id, location, current_temp in rows:
                t = float(current_temp)
                if t >= 90:
                    risk, score, action = "CRITICAL", 100, "Immediate shutdown and onsite inspection"
                elif t >= 80:
                    risk, score, action = "HIGH", 80, "Dispatch technician within 2 hours"
                elif t >= 75:
                    risk, score, action = "MEDIUM", 60, "Schedule maintenance within 24 hours"
                else:
                    risk, score, action = "NORMAL", 20, "Monitor only"

                cur.execute(
                    """
                    INSERT INTO sensor_maintenance_queue
                    (device_id, location, current_temp, risk_level, priority_score, recommended_action, status)
                    VALUES (%s,%s,%s,%s,%s,%s,'OPEN')
                    """,
                    (device_id, location, t, risk, score, action),
                )

            conn.commit()
            return f"inserted={len(rows)}"
        finally:
            cur.close()
            conn.close()

    classify_and_insert()


manual_sensor_maintenance_classifier()
