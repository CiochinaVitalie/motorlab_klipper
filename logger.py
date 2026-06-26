import csv
import os
import time


class MotorLabLogger:
    def __init__(self, base_path):
        self.base_path = os.path.expanduser(base_path)
        os.makedirs(self.base_path, exist_ok=True)

    def open_csv(self, test_name, axis):
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = "%s_%s_%s.csv" % (ts, axis, test_name.lower())
        path = os.path.join(self.base_path, filename)
        return CsvLog(path)


class CsvLog:
    def __init__(self, path):
        self.path = path
        self.file = open(path, "w", newline="")
        self.writer = csv.writer(self.file)
        self.header_written = False

    def write(self, row):
        if not self.header_written:
            self.writer.writerow(list(row.keys()))
            self.header_written = True
        self.writer.writerow([row[k] for k in row.keys()])
        self.file.flush()

    def close(self):
        self.file.close()
