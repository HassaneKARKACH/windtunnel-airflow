"""Load test DAG: each run holds a chosen number of worker slots for a chosen time."""

import time

from airflow.sdk import Param, dag, task


@dag(
    schedule=None,
    params={
        "tasks": Param(10, type="integer", minimum=1),
        "seconds": Param(60, type="integer", minimum=0),
    },
)
def load_test():
    @task
    def slots(params):
        return list(range(params["tasks"]))

    @task
    def hold(slot, params):
        # A load test task computes nothing: it only keeps its worker slot busy.
        time.sleep(params["seconds"])

    hold.expand(slot=slots())


load_test()
