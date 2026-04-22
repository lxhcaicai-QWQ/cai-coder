import time

from agent.cron.service import _now_ms, CronSchedule, _compute_next_run


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
