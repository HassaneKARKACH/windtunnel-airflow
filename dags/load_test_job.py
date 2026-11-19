"""Load test DAG: each task acts like a client of an external job, busy at startup then idle."""

import time

from airflow.sdk import Param, dag, task


@dag(
    schedule=None,
    params={
        "tasks": Param(10, type="integer", minimum=1),
        "startup_seconds": Param(10, type="integer", minimum=0),
        "seconds": Param(60, type="integer", minimum=0),
    },
)
def load_test_job():
    @task
    def slots(params):
        return list(range(params["tasks"]))

    @task
    def drive(slot, params):
        # Starting a job client burns CPU on the worker: spin instead of sleeping.
        startup_end = time.monotonic() + params["startup_seconds"]
        while time.monotonic() < startup_end:
            pass
        # Then the job runs elsewhere: the slot stays taken but the worker is idle.
        time.sleep(params["seconds"])

    drive.expand(slot=slots())


load_test_job()
