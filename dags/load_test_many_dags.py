"""Load test DAGs: a chosen number of idle DAGs for the dag-processor to parse."""

import os

from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import DAG

# The count is read at parse time, so it cannot be a run parameter.
dag_count = int(os.environ.get("LOAD_TEST_DAG_COUNT", "0"))

for number in range(dag_count):
    with DAG(f"load_test_many_dags_{number:04d}", schedule=None):
        EmptyOperator(task_id="idle")
