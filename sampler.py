# sampler.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

INTERVAL_MIN: int = 5


class MeasType(Enum):
    SPO2 = 1
    HR = 2
    TEMP = 3

@dataclass
class Measurement:
    measurement_time: datetime = datetime.min
    measurement_type: MeasType = MeasType.SPO2
    value: float = 0.0


def get_interval(_time: datetime, interval_min: int) -> datetime:
    if interval_min <= 0:
        raise ValueError("Expected positive interval [min]")

    if interval_min >= 60:
        raise NotImplementedError("Intervals [min] higher than 1 [hour] are not supported")

    if (_time.second == 0 and
        _time.minute in [i * interval_min for i in range(60 // interval_min)]):
        return _time

    _minute: datetime.minute = (_time.minute // interval_min) * interval_min
    _from: datetime = _time.replace(minute=_minute, second=0, microsecond=0)
    return _from + timedelta(minutes=interval_min)


def sample_measurements(unsampled: list[Measurement]) -> dict[MeasType, list[Measurement]]:
    sampled: dict[MeasType, list[Measurement]] = {}
    unsampled.sort(key=lambda x: x.measurement_time)

    measurement: Measurement
    for measurement in unsampled:
        _type = measurement.measurement_type
        measurement.measurement_time = get_interval(measurement.measurement_time, INTERVAL_MIN)

        # Add first interval
        if sampled.get(_type) is None:
            sampled[_type] = [measurement]
            continue

        # Update existing interval
        last: Measurement = sampled[_type][-1]
        if last.measurement_time == measurement.measurement_time:
            sampled[_type][-1] = measurement
            continue

        # Append new interval
        sampled[_type].append(measurement)

    return sampled


def main():
    example_input: list[Measurement] = [
        Measurement(datetime(2017, 1, 13, 10, 4, 45), MeasType.TEMP, 35.79),
        Measurement(datetime(2017, 1, 13, 10, 1, 18), MeasType.SPO2, 98.78),
        Measurement(datetime(2017, 1, 13, 10, 9,  7), MeasType.TEMP, 35.01),
        Measurement(datetime(2017, 1, 13, 10, 3, 34), MeasType.SPO2, 96.49),
        Measurement(datetime(2017, 1, 13, 10, 2,  1), MeasType.TEMP, 35.82),
        Measurement(datetime(2017, 1, 13, 10, 5,  0), MeasType.SPO2, 97.17),
        Measurement(datetime(2017, 1, 13, 10, 5,  1), MeasType.SPO2, 95.08)
    ]
    for _, v in sample_measurements(example_input).items():
        for sampled_measurement in v:
            print(sampled_measurement)


if __name__ == "__main__":
    main()
