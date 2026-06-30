class MetricsCalculator:
    """Compute PTZ motion metrics from sensor and encoder samples."""

    def step_response(self, samples):
        if not samples:
            return {}
        return {
            "sample_count": len(samples),
            "peak_error_deg": self._max_abs(samples, "error_deg"),
            "peak_accel": self._max_abs(samples, "accel_g"),
            "rms_accel": self.rms_accel(samples),
            "settling_time_ms": self._first_value(samples, "settle_time_ms"),
        }

    def settling_time_ms(self, samples):
        return self._first_value(samples, "settle_time_ms")

    def peak_accel(self, samples):
        return self._max_abs(samples, "accel_g")

    def rms_accel(self, samples):
        values = self._values(samples, "accel_g")
        if not values:
            return None
        return (sum(v * v for v in values) / float(len(values))) ** 0.5

    def position_error_deg(self, target_deg, actual_deg):
        if target_deg is None or actual_deg is None:
            return None
        return actual_deg - target_deg

    def _values(self, samples, key):
        values = []
        for sample in samples:
            value = self._sample_value(sample, key)
            if value is not None:
                values.append(float(value))
        return values

    def _max_abs(self, samples, key):
        values = self._values(samples, key)
        if not values:
            return None
        return max(abs(v) for v in values)

    def _first_value(self, samples, key):
        for sample in samples:
            value = self._sample_value(sample, key)
            if value is not None:
                return float(value)
        return None

    def _sample_value(self, sample, key):
        if isinstance(sample, dict):
            return sample.get(key)
        if isinstance(sample, (list, tuple)):
            index_map = {
                "error_deg": 0,
                "accel_g": 1,
                "settle_time_ms": 2,
            }
            index = index_map.get(key)
            if index is not None and len(sample) > index:
                return sample[index]
        return None
