import pytest
import time_machine

time_machine.naive_mode = time_machine.NaiveMode.UTC


@pytest.fixture(name="time_machine")
def time_machine_fixture():
    return time_machine


@pytest.fixture(name="freeze_time")
def freeze_time_fixture():
    def freeze_time(arg):
        return time_machine.travel(arg)

    return freeze_time
