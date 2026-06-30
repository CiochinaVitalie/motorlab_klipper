import csv
import os


class CsvExporter:
    """Write PTZ test results and derived metrics to CSV."""

    def export_run(self, path, rows):
        rows = list(rows)
        if not rows:
            return path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def export_summary(self, path, summary):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["key", "value"])
            for key, value in summary.items():
                writer.writerow([key, value])
        return path
