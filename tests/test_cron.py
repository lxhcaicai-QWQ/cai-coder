import json
import time

from agent.cron.service import _now_ms, CronSchedule, _compute_next_run, CronJob, CronJobState, CronService


def test_now_ms():
    assert abs(time.time() * 1000 - _now_ms()) < 100


def test_compute_next_run_every():
    every_ms = 30*1000
    every_sched = CronSchedule(
        kind="every",
        every_ms=every_ms
    )
    assert abs(time.time() * 1000 + every_ms - _compute_next_run(every_sched,_now_ms())) < 10


def test_compute_next_run_at():
    at_ms = 10*1000 + _now_ms()
    at_sched = CronSchedule(
        kind="at",
        at_ms=at_ms
    )
    assert abs(at_ms - _compute_next_run(at_sched,_now_ms())) < 10

def test_add_cronjob(tmp_path):

    service = CronService(workspace=tmp_path)

    at_sched = CronSchedule(
        kind="at",
        at_ms=10*1000 + _now_ms()
    )

    added_job = service.add_job("test",schedule=at_sched,payload={"version":"1.0"})

    assert added_job.enabled
    assert added_job.payload == {"version":"1.0"}
    assert added_job.id is not None
    assert abs(added_job.state.next_run_at_ms - (10*1000 + _now_ms())) < 10

    assert len(service._jobs)== 1

def test_list_jobs(tmp_path):
    service = CronService(workspace=tmp_path)

    at_sched = CronSchedule(
        kind="at",
        at_ms=10*1000 + _now_ms()
    )

    test1 = service.add_job("test1",schedule=at_sched,payload={"version":"1.0"})
    test2 = service.add_job("test2",schedule=at_sched,payload={"version":"1.0"})
    test3 = service.add_job("test3",schedule=at_sched,payload={"version":"1.0"})

    jobs = service.list_jobs()
    assert len(jobs) == 3
    assert jobs == [test1, test2, test3]


def test_remove_job(tmp_path):
    service = CronService(tmp_path)
    at_sched = CronSchedule(
        kind="at",
        at_ms=10*1000 + _now_ms()
    )

    test1 = service.add_job("test1",schedule=at_sched,payload={"version":"1.0"})
    test2 = service.add_job("test2",schedule=at_sched,payload={"version":"1.0"})
    test3 = service.add_job("test3",schedule=at_sched,payload={"version":"1.0"})

    jobs = service.list_jobs()
    assert len(jobs) == 3
    assert jobs == [test1, test2, test3]

    service.remove_job(test2.id)
    jobs = service.list_jobs()
    assert len(jobs) == 2
    assert jobs == [test1 , test3]


def test_cron_execute_job_at(tmp_path):
    def call_job(job: CronJob):
        print(f"  -> Processing business: {job.payload}")

    service = CronService(
        workspace=tmp_path,
        on_job=call_job
    )

    at_sched = CronSchedule(
        kind="at",
        at_ms = _now_ms()
    )
    job = CronJob(
        name="test",
        schedule=at_sched,
        payload={
            "task":"do a job"
        },
        state=CronJobState(
            next_run_at_ms=_compute_next_run(at_sched, _now_ms())
        )
    )
    assert job.enabled
    service._execute_job(job)
    assert not job.enabled
    assert not job.state.next_run_at_ms


def test_cron_execute_job_every(tmp_path):
    def call_job(job: CronJob):
        print(f"  -> Processing business: {job.payload}")

    service = CronService(
        on_job=call_job,
        workspace=tmp_path
    )

    every_ms = 30*1000
    every_sched = CronSchedule(
        kind="every",
        every_ms=every_ms
    )

    job = CronJob(
        name="test",
        schedule=every_sched,
        payload={
            "task":"do a job"
        },
        state=CronJobState(
            next_run_at_ms=_compute_next_run(every_sched, _now_ms())
        )
    )
    assert job.enabled
    service._execute_job(job)

    assert job.enabled
    assert abs(job.state.next_run_at_ms -( every_ms +_now_ms())) < 10


def test_cron_service_all(tmp_path):
    def call_job(job: CronJob):
        print(f"  -> Processing business: {job.payload}")

    service = CronService(
        on_job=call_job,
        max_sleep_ms = 2000,
        workspace=tmp_path
    )

    at_sched = CronSchedule(
        kind="at",
        at_ms=500 + _now_ms()
    )
    every_sched = CronSchedule(
        kind="every",
        every_ms=1000
    )
    test1 = service.add_job("test1",schedule=at_sched,payload={"version":"1.0"})
    test2 = service.add_job("test2",schedule=every_sched,payload={"version":"1.0"})
    test3 = service.add_job("test3",schedule=at_sched,payload={"version":"1.0"})
    service.start()
    test4 = service.add_job("test4",schedule=at_sched,payload={"version":"1.0"})

    time.sleep(3)
    service.stop()

def test_cron_job_path(tmp_path):
    service = CronService(workspace=tmp_path)
    assert service._get_corn_job_path() == tmp_path / "cron" / "cron.json"


CRON_JOB_JSON = """
[
  {
    "id": "d70506a5",
    "name": "test1",
    "enabled": [
      true
    ],
    "schedule": {
      "kind": "at",
      "every_ms": 0,
      "at_ms": 1777132479751
    },
    "state": {
      "next_run_at_ms": 1777132479751,
      "last_run_at_ms": null,
      "last_status": null,
      "last_error": null
    },
    "payload": {
      "version": "1.0"
    }
  },
  {
    "id": "3f454aa3",
    "name": "test2",
    "enabled": [
      true
    ],
    "schedule": {
      "kind": "every",
      "every_ms": 1000,
      "at_ms": 0
    },
    "state": {
      "next_run_at_ms": 1777132480251,
      "last_run_at_ms": null,
      "last_status": null,
      "last_error": null
    },
    "payload": {
      "version": "1.0"
    }
  }
]
"""

def test_save(tmp_path):

    at_sched = CronSchedule(
        kind="at",
        at_ms=500 + _now_ms()
    )
    every_sched = CronSchedule(
        kind="every",
        every_ms=1000
    )

    service = CronService(workspace=tmp_path)
    service.add_job("test1",schedule=at_sched,payload={"version":"1.0"})
    service.add_job("test2",schedule=every_sched,payload={"version":"1.0"})
    service._save()

    corn_path = tmp_path / "cron" / "cron.json"
    text = corn_path.read_text()

    cronjob_list = json.loads(text)
    assert cronjob_list[0]["name"] == "test1"
    assert cronjob_list[0]["schedule"]["kind"] == "at"
    assert cronjob_list[1]["name"] == "test2"
    assert cronjob_list[1]["schedule"]["kind"] == "every"

    print()

def test_load(tmp_path):
    corn_path = tmp_path / "cron" / "cron.json"
    corn_path.parent.mkdir(parents=True, exist_ok=True)
    corn_path.write_text(CRON_JOB_JSON,encoding="utf-8")

    service = CronService(workspace=tmp_path)
    result: list[CronJob] = service._load()

    jobs = [item.to_dict() for item in result]
    job_list = json.loads(CRON_JOB_JSON)
    assert jobs == job_list
