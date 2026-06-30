import csv


class ScoreCalculator:
    """Rank PTZ parameter sets and choose the best one."""

    def score_run(self, metrics):
        if not metrics:
            return None

        score = 0.0

        for key in (
            "final_error_deg",
            "forward_final_error_deg",
            "return_final_error_deg",
            "reverse_final_error_deg",
            "reverse_return_final_error_deg",
        ):
            score += 1000.0 * self._abs(metrics.get(key))

        for key in (
            "forward_peak_error_deg",
            "return_peak_error_deg",
            "peak_error_deg",
        ):
            score += 250.0 * self._abs(metrics.get(key))

        for key in (
            "forward_settle_time_ms",
            "return_settle_time_ms",
            "settle_time_ms",
        ):
            value = self._num(metrics.get(key))
            if value is not None:
                score += 0.01 * value

        for key in (
            "peak_accel",
            "rms_accel",
        ):
            value = self._num(metrics.get(key))
            if value is not None:
                score += 10.0 * value

        for key in ("motor_temp_c", "driver_temp_c"):
            value = self._num(metrics.get(key))
            if value is not None and value > 60.0:
                score += 20.0 * (value - 60.0)

        if metrics.get("status") not in (None, "OK"):
            score += 1_000_000.0

        return score

    def compare_runs(self, runs):
        scored = []
        for run in runs:
            if isinstance(run, dict):
                metrics = dict(run)
                score = self.score_run(metrics)
                if score is None:
                    continue
                metrics["score"] = score
                scored.append(metrics)
        scored.sort(key=lambda item: item["score"])
        return scored

    def best_run(self, runs):
        scored = self.compare_runs(runs)
        if not scored:
            return None
        return scored[0]

    def load_csv(self, path):
        with open(path, newline="") as fh:
            reader = csv.DictReader(fh)
            return list(reader)

    def score_csv(self, path):
        rows = self.load_csv(path)
        scored = self.compare_runs(rows)
        return scored

    def _num(self, value):
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _abs(self, value):
        num = self._num(value)
        if num is None:
            return 0.0
        return abs(num)
