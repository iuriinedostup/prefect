import cloudpickle
import os
import pendulum
import subprocess
import tempfile

import pytest

from prefect import context, Flow
from prefect.engine import signals
from prefect.tasks.templates import StringFormatterTask
from prefect.utilities.debug import raise_on_exception


def test_string_formatter_simply_formats():
    task = StringFormatterTask(template="{name} is from {place}")
    with Flow(name="test") as f:
        ans = task(name="Ford", place="Betelgeuse")
    res = f.run()
    assert res.is_successful()
    assert res.result[ans].result == "Ford is from Betelgeuse"


def test_string_formatter_can_be_provided_template_at_runtime():
    task = StringFormatterTask()
    with Flow(name="test") as f:
        ans = task(template="{name} is from {place}", name="Ford", place="Betelgeuse")
    res = f.run()
    assert res.is_successful()
    assert res.result[ans].result == "Ford is from Betelgeuse"


def test_string_formatter_formats_from_context():
    task = StringFormatterTask(template="I am {task_name}", name="foo")
    f = Flow(name="test", tasks=[task])
    res = f.run()
    assert res.is_successful()
    assert res.result[task].result == "I am foo"


def test_string_formatter_fails_in_expected_ways():
    t1 = StringFormatterTask(template="{name} is from {place}")
    t2 = StringFormatterTask(template="{0} is from {1}")
    f = Flow(name="test", tasks=[t1, t2])
    res = f.run()

    assert res.is_failed()
    assert isinstance(res.result[t1].result, KeyError)
    assert isinstance(res.result[t2].result, IndexError)