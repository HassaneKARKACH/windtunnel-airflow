"""Load test DAG: each run parks a chosen number of deferred sensors on the triggerer."""

from datetime import datetime, timedelta, timezone

from airflow.providers.standard.sensors.date_time import DateTimeSensorAsync
from airflow.sdk import Param, dag, task


@dag(
    schedule=None,
    params={
        "sensors": Param(10, type="integer", minimum=1),
        "seconds": Param(60, type="integer", minimum=0),
    },
)
def load_test_deferred():
    @task
    def wake_times(params):
        # One shared wake time: all sensors resume at once and ask for a worker slot together.
        wake_time = datetime.now(timezone.utc) + timedelta(seconds=params["seconds"])
        return [wake_time.isoformat()] * params["sensors"]

    DateTimeSensorAsync.partial(task_id="wait").expand(target_time=wake_times())


load_test_deferred()
