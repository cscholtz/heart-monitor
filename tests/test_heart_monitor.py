"""Unit tests for the HeartMonitor and HeartRateReading classes."""

import pytest
from datetime import datetime
from heart_monitor import HeartMonitor, HeartRateReading


class TestHeartRateReading:
    def test_valid_reading(self):
        reading = HeartRateReading(75)
        assert reading.bpm == 75
        assert isinstance(reading.timestamp, datetime)

    def test_explicit_timestamp(self):
        ts = datetime(2024, 1, 1, 12, 0, 0)
        reading = HeartRateReading(80, timestamp=ts)
        assert reading.timestamp == ts

    def test_invalid_zero_bpm(self):
        with pytest.raises(ValueError):
            HeartRateReading(0)

    def test_invalid_negative_bpm(self):
        with pytest.raises(ValueError):
            HeartRateReading(-10)

    def test_repr(self):
        ts = datetime(2024, 6, 15, 8, 30, 0)
        reading = HeartRateReading(72, timestamp=ts)
        assert "72" in repr(reading)


class TestHeartMonitorRecording:
    def setup_method(self):
        self.monitor = HeartMonitor()

    def test_starts_empty(self):
        assert self.monitor.count == 0
        assert self.monitor.readings == []
        assert self.monitor.latest is None

    def test_add_single_reading(self):
        reading = self.monitor.add_reading(75)
        assert self.monitor.count == 1
        assert reading.bpm == 75

    def test_add_multiple_readings(self):
        self.monitor.add_reading(70)
        self.monitor.add_reading(80)
        self.monitor.add_reading(90)
        assert self.monitor.count == 3

    def test_latest_reading(self):
        self.monitor.add_reading(70)
        self.monitor.add_reading(95)
        assert self.monitor.latest.bpm == 95

    def test_readings_are_in_order(self):
        self.monitor.add_reading(60)
        self.monitor.add_reading(70)
        self.monitor.add_reading(80)
        bpms = [r.bpm for r in self.monitor.readings]
        assert bpms == [60, 70, 80]

    def test_readings_returns_copy(self):
        self.monitor.add_reading(70)
        readings = self.monitor.readings
        readings.append(HeartRateReading(999))
        assert self.monitor.count == 1  # internal list unchanged

    def test_add_reading_with_explicit_timestamp(self):
        ts = datetime(2024, 3, 10, 9, 0, 0)
        reading = self.monitor.add_reading(65, timestamp=ts)
        assert reading.timestamp == ts

    def test_invalid_reading_not_stored(self):
        with pytest.raises(ValueError):
            self.monitor.add_reading(-5)
        assert self.monitor.count == 0


class TestHeartMonitorStatistics:
    def setup_method(self):
        self.monitor = HeartMonitor()

    def test_statistics_empty(self):
        assert self.monitor.average_bpm() is None
        assert self.monitor.min_bpm() is None
        assert self.monitor.max_bpm() is None
        assert self.monitor.std_bpm() is None

    def test_average_bpm(self):
        self.monitor.add_reading(60)
        self.monitor.add_reading(80)
        self.monitor.add_reading(100)
        assert self.monitor.average_bpm() == 80.0

    def test_min_bpm(self):
        self.monitor.add_reading(75)
        self.monitor.add_reading(55)
        self.monitor.add_reading(90)
        assert self.monitor.min_bpm() == 55

    def test_max_bpm(self):
        self.monitor.add_reading(75)
        self.monitor.add_reading(55)
        self.monitor.add_reading(110)
        assert self.monitor.max_bpm() == 110

    def test_std_bpm_single_reading(self):
        self.monitor.add_reading(75)
        assert self.monitor.std_bpm() is None

    def test_std_bpm_multiple_readings(self):
        self.monitor.add_reading(60)
        self.monitor.add_reading(80)
        std = self.monitor.std_bpm()
        assert std is not None
        assert std > 0


class TestHeartMonitorStatus:
    def setup_method(self):
        self.monitor = HeartMonitor()

    def test_normal_range(self):
        for bpm in [60, 75, 100]:
            assert self.monitor.is_normal(bpm)
            assert self.monitor.status(bpm) == "normal"

    def test_bradycardia(self):
        for bpm in [59, 45, 30]:
            assert self.monitor.is_bradycardia(bpm)
            assert not self.monitor.is_normal(bpm)
            assert self.monitor.status(bpm) == "bradycardia"

    def test_tachycardia(self):
        for bpm in [101, 130, 180]:
            assert self.monitor.is_tachycardia(bpm)
            assert not self.monitor.is_normal(bpm)
            assert self.monitor.status(bpm) == "tachycardia"

    def test_boundary_60_is_normal(self):
        assert self.monitor.is_normal(60)
        assert not self.monitor.is_bradycardia(60)

    def test_boundary_100_is_normal(self):
        assert self.monitor.is_normal(100)
        assert not self.monitor.is_tachycardia(100)


class TestHeartMonitorAbnormalDetection:
    def setup_method(self):
        self.monitor = HeartMonitor()

    def test_no_abnormal_readings_when_all_normal(self):
        self.monitor.add_reading(70)
        self.monitor.add_reading(80)
        self.monitor.add_reading(90)
        assert self.monitor.abnormal_readings() == []

    def test_detects_low_readings(self):
        self.monitor.add_reading(75)
        self.monitor.add_reading(45)
        abnormal = self.monitor.abnormal_readings()
        assert len(abnormal) == 1
        assert abnormal[0].bpm == 45

    def test_detects_high_readings(self):
        self.monitor.add_reading(75)
        self.monitor.add_reading(150)
        abnormal = self.monitor.abnormal_readings()
        assert len(abnormal) == 1
        assert abnormal[0].bpm == 150

    def test_detects_mixed_abnormal(self):
        self.monitor.add_reading(40)
        self.monitor.add_reading(75)
        self.monitor.add_reading(120)
        abnormal = self.monitor.abnormal_readings()
        assert len(abnormal) == 2


class TestHeartMonitorSummary:
    def setup_method(self):
        self.monitor = HeartMonitor()

    def test_summary_empty(self):
        assert self.monitor.summary() == "No readings recorded."

    def test_summary_normal(self):
        self.monitor.add_reading(75)
        self.monitor.add_reading(80)
        summary = self.monitor.summary()
        assert "2" in summary
        assert "normal" in summary

    def test_summary_includes_abnormal_count(self):
        self.monitor.add_reading(75)
        self.monitor.add_reading(150)
        summary = self.monitor.summary()
        assert "Abnormal" in summary
        assert "1" in summary

    def test_summary_no_abnormal_section_when_all_normal(self):
        self.monitor.add_reading(70)
        self.monitor.add_reading(80)
        summary = self.monitor.summary()
        assert "Abnormal" not in summary
