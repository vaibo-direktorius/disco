# test_sampler.py
from datetime import datetime, timedelta
import pytest
import sampler

START_TIME: datetime = datetime(2024, 5, 13, 20, 0, 42)

@pytest.mark.parametrize("interval_min", range(1, 60))
def test_get_interval_valid(interval_min: int) -> None:
    expected_time: datetime = datetime(2024, 5, 13, 20, 0, 0) + timedelta(minutes=interval_min)
    assert sampler.get_interval(START_TIME, interval_min) == expected_time


def test_get_interval_negative() -> None:
    interval_min: int = -1
    with pytest.raises(ValueError):
        sampler.get_interval(START_TIME, interval_min)


def test_get_interval_zero() -> None:
    interval_min: int = 0
    with pytest.raises(ValueError):
        sampler.get_interval(START_TIME, interval_min)


def test_get_interval_high() -> None:
    interval_min: int = 60
    with pytest.raises(NotImplementedError):
        sampler.get_interval(START_TIME, interval_min)


def test_get_interval_exact_time() -> None:
    """
    Calculated interval matches current time
    """
    _start_time: datetime = datetime(2024, 5, 13, 20, 10, 0)
    assert sampler.get_interval(_start_time, 10) == _start_time


def test_get_interval_roll_h() -> None:
    """
    Start time is set to a time before "rolling" hour, expected to get hour + 1 after interval
    E.g. 05/13/2024 08:58:51 with interval [min] = 5 would result in 05/13/2024 09:00:00
    """
    _start_time: datetime = datetime(2024, 5, 13, 8, 58, 51)
    assert sampler.get_interval(_start_time, 5) == datetime(2024, 5, 13, 9, 0, 0)


def test_get_interval_roll_d() -> None:
    """
    Start time is set to a time before "rolling" day, expected to get day + 1 after interval
    E.g. 05/13/2024 23:58:51 with interval [min] = 5 would result in 05/14/2024 00:00:00
    """
    _start_time: datetime = datetime(2024, 5, 13, 23, 58, 51)
    assert sampler.get_interval(_start_time, 5) == datetime(2024, 5, 14, 0, 0, 0)


def test_get_interval_roll_m() -> None:
    """
    Start time is set to a time before "rolling" month, expected to get month + 1 after interval
    E.g. 05/31/2024 23:58:51 with interval [min] = 5 would result in 06/01/2024 00:00:00
    """
    _start_time: datetime = datetime(2024, 5, 31, 23, 58, 51)
    assert sampler.get_interval(_start_time, 5) == datetime(2024, 6, 1, 0, 0, 0)


def test_get_interval_roll_y() -> None:
    """
    Start time is set to a time before "rolling" year, expected to get year + 1 after interval
    E.g. 12/31/2024 23:58:51 with interval [min] = 5 would result in 01/01/2025 00:00:00
    """
    _start_time: datetime = datetime(2024, 12, 31, 23, 58, 51)
    assert sampler.get_interval(_start_time, 5) == datetime(2025, 1, 1, 0, 0, 0)


@pytest.fixture(name="diff_measurements")
def fixture_diff_measurements() -> list[sampler.Measurement]:
    """
    Measurements with different Measurement Types (see sampler.MeasType)
    """
    return [
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 35.79),
        sampler.Measurement(datetime(2017, 1, 13, 10, 1, 18), sampler.MeasType.SPO2, 98.78),
        sampler.Measurement(datetime(2017, 1, 13, 10, 2, 28), sampler.MeasType.HR, 98.78)
    ]

@pytest.fixture(name="update_measurements")
def fixture_update_measurements() -> list[sampler.Measurement]:
    """
    Repetetive measurements, with same Measurement Types. Fixture used to check interval update
    """
    return [
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 35.79),
        sampler.Measurement(datetime(2017, 1, 13, 10, 1, 18), sampler.MeasType.SPO2, 98.78),
        sampler.Measurement(datetime(2017, 1, 13, 10, 2, 28),  sampler.MeasType.HR, 98.78),
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 79.35),
        sampler.Measurement(datetime(2017, 1, 13, 10, 1, 18), sampler.MeasType.SPO2, 14.14),
        sampler.Measurement(datetime(2017, 1, 13, 10, 2, 28),  sampler.MeasType.HR, 29.84),
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 46), sampler.MeasType.TEMP, 12.34),
        sampler.Measurement(datetime(2017, 1, 13, 10, 1, 19), sampler.MeasType.SPO2, 55.55),
        sampler.Measurement(datetime(2017, 1, 13, 10, 2, 29),  sampler.MeasType.HR, 35.79)
    ]

@pytest.fixture(name="example_measurements")
def fixture_example_measurements() -> list[sampler.Measurement]:
    """
    Example measurements refer to a list of measurements, provided in `DataSampling_Python.pdf` file
    """
    return [
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 35.79),
        sampler.Measurement(datetime(2017, 1, 13, 10, 1, 18), sampler.MeasType.SPO2, 98.78),
        sampler.Measurement(datetime(2017, 1, 13, 10, 9,  7), sampler.MeasType.TEMP, 35.01),
        sampler.Measurement(datetime(2017, 1, 13, 10, 3, 34), sampler.MeasType.SPO2, 96.49),
        sampler.Measurement(datetime(2017, 1, 13, 10, 2,  1), sampler.MeasType.TEMP, 35.82),
        sampler.Measurement(datetime(2017, 1, 13, 10, 5,  0), sampler.MeasType.SPO2, 97.17),
        sampler.Measurement(datetime(2017, 1, 13, 10, 5,  1), sampler.MeasType.SPO2, 95.08)
    ]


def test_sample_measurements_empty() -> None:
    assert not sampler.sample_measurements([])


def test_sample_measurements_one(diff_measurements: list[sampler.Measurement]) -> None:
    expected_sample: dict[sampler.MeasType, list[sampler.Measurement]] = {
        sampler.MeasType.TEMP: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.TEMP, 35.79)]
    }
    assert sampler.sample_measurements(diff_measurements[:1]) == expected_sample


def test_sample_measurements_two(diff_measurements: list[sampler.Measurement]) -> None:
    expected_sample: dict[sampler.MeasType, list[sampler.Measurement]] = {
        sampler.MeasType.TEMP: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.TEMP, 35.79)],
        sampler.MeasType.SPO2: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.SPO2, 98.78)]
    }
    assert sampler.sample_measurements(diff_measurements[:2]) == expected_sample


def test_sample_measurements_three(diff_measurements: list[sampler.Measurement]) -> None:
    expected_sample: dict[sampler.MeasType, list[sampler.Measurement]] = {
        sampler.MeasType.TEMP: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.TEMP, 35.79)],
        sampler.MeasType.SPO2: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.SPO2, 98.78)],
        sampler.MeasType.HR: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.HR, 98.78)]
    }
    assert sampler.sample_measurements(diff_measurements[:3]) == expected_sample


def test_sample_measurements_update(update_measurements: list[sampler.Measurement]) -> None:
    expected_sample: dict[sampler.MeasType, list[sampler.Measurement]] = {
        sampler.MeasType.SPO2: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.SPO2, 55.55)],
        sampler.MeasType.HR: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0),   sampler.MeasType.HR, 35.79)],
        sampler.MeasType.TEMP: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.TEMP, 12.34)]
    }
    assert sampler.sample_measurements(update_measurements) == expected_sample


def test_sample_measurements_same() -> None:
    measurements: list[sampler.Measurement] = [
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 11.11),
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 22.22),
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 33.33),
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 44.44),
        sampler.Measurement(datetime(2017, 1, 13, 10, 4, 45), sampler.MeasType.TEMP, 55.55)
    ]
    expected_sample: dict[sampler.MeasType, list[sampler.Measurement]] = {
        sampler.MeasType.TEMP: [sampler.Measurement(datetime(2017, 1, 13, 10, 5, 0), sampler.MeasType.TEMP, 55.55)]
    }
    assert sampler.sample_measurements(measurements) == expected_sample


def test_sample_measurements_valid(example_measurements: list[sampler.Measurement]) -> None:
    expected_sample: dict[sampler.MeasType, list[sampler.Measurement]] = {
        sampler.MeasType.TEMP: [
            sampler.Measurement(datetime(2017, 1, 13, 10,  5, 0), sampler.MeasType.TEMP, 35.79),
            sampler.Measurement(datetime(2017, 1, 13, 10, 10, 0), sampler.MeasType.TEMP, 35.01)
        ],
        sampler.MeasType.SPO2: [
            sampler.Measurement(datetime(2017, 1, 13, 10,  5, 0), sampler.MeasType.SPO2, 97.17),
            sampler.Measurement(datetime(2017, 1, 13, 10, 10, 0), sampler.MeasType.SPO2, 95.08)
        ]
    }
    assert sampler.sample_measurements(example_measurements) == expected_sample


def test_sample_measurements_reversed(example_measurements: list[sampler.Measurement]) -> None:
    expected_sample: dict[sampler.MeasType, list[sampler.Measurement]] = {
        sampler.MeasType.TEMP: [
            sampler.Measurement(datetime(2017, 1, 13, 10,  5, 0), sampler.MeasType.TEMP, 35.79),
            sampler.Measurement(datetime(2017, 1, 13, 10, 10, 0), sampler.MeasType.TEMP, 35.01)
        ],
        sampler.MeasType.SPO2: [
            sampler.Measurement(datetime(2017, 1, 13, 10,  5, 0), sampler.MeasType.SPO2, 97.17),
            sampler.Measurement(datetime(2017, 1, 13, 10, 10, 0), sampler.MeasType.SPO2, 95.08)
        ]
    }
    assert sampler.sample_measurements(example_measurements[::1]) == expected_sample
