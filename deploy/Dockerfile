# Build from the repo root: the DAGs live outside this folder.
# Keep the base tag equal to airflowVersion in values.yaml.
FROM apache/airflow:3.2.2

COPY --chown=airflow:root dags/ /opt/airflow/dags/
