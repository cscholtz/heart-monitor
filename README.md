# heart-monitor

A Python library for monitoring heart rate readings over time.

## Features

- Record heart rate readings with automatic timestamps
- Detect abnormal heart rate conditions (bradycardia / tachycardia)
- Compute statistics: average, min, max, standard deviation
- Retrieve a human-readable summary of all readings

## Heart rate thresholds

| Condition     | Range        |
|---------------|--------------|
| Bradycardia   | < 60 bpm     |
| Normal        | 60 – 100 bpm |
| Tachycardia   | > 100 bpm    |

## Usage

```python
from heart_monitor import HeartMonitor

monitor = HeartMonitor()

# Record readings
monitor.add_reading(72)
monitor.add_reading(68)
monitor.add_reading(110)  # tachycardia

# Check the latest reading
print(monitor.latest.bpm)          # 110
print(monitor.status(110))         # "tachycardia"

# Statistics
print(monitor.average_bpm())       # 83.33...
print(monitor.min_bpm())           # 68
print(monitor.max_bpm())           # 110

# Abnormal readings
for r in monitor.abnormal_readings():
    print(r.bpm, monitor.status(r.bpm))

# Full summary
print(monitor.summary())
```

## Running tests

```bash
python -m pytest tests/ -v
```