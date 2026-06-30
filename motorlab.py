import glob
import os
import shutil
import time

from .analysis.csv_export import CsvExporter
from .analysis.score import ScoreCalculator
from .logger import MotorLabLogger
from .encoder import MotorLabEncoder
from .sensors.temperature import TemperatureMonitor
from .sensors.adxl345 import KlipperADXL345
from .tests.speed import SpeedTest
from .tests.acceleration import AccelerationTest
from .tests.repeatability import RepeatabilityTest
from .tests.backlash import BacklashTest
from .tests.endurance import EnduranceTest
from .tests.homing import HomingTest
from .tests.ptz_step_response import PTZStepResponseTest
from .tests.ptz_speed_sweep import PTZSpeedSweepTest
from .tests.ptz_accel_sweep import PTZAccelSweepTest
from .tests.ptz_settling import PTZSettlingTest
from .tests.ptz_backlash import PTZBacklashTest
from .tests.ptz_endurance import PTZEnduranceTest


class MotorLab:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object("gcode")
        self.mode = config.get("mode", "accelerometer_only").strip().lower()
        self.log_path = os.path.expanduser(
            config.get("log_path", "~/printer_data/logs/motorlab")
        )
        os.makedirs(self.log_path, exist_ok=True)

        self.accelerometer = KlipperADXL345(self)
        self.logger = None
        self.encoder = None
        self.temperature = None
        self.score = ScoreCalculator()
        self.csv_exporter = CsvExporter()

        if self.mode in ("ptz", "full"):
            self.logger = MotorLabLogger(self.log_path)
            self.encoder = MotorLabEncoder(config)
            self.temperature = TemperatureMonitor(config)

        self.tests = {
            "SPEED": SpeedTest,
            "ACCELERATION": AccelerationTest,
            "REPEATABILITY": RepeatabilityTest,
            "BACKLASH": BacklashTest,
            "ENDURANCE": EnduranceTest,
            "HOMING": HomingTest,
            "PTZ_STEP_RESPONSE": PTZStepResponseTest,
            "PTZ_SPEED_SWEEP": PTZSpeedSweepTest,
            "PTZ_ACCEL_SWEEP": PTZAccelSweepTest,
            "PTZ_SETTLING": PTZSettlingTest,
            "PTZ_BACKLASH": PTZBacklashTest,
            "PTZ_ENDURANCE": PTZEnduranceTest,
        }

        self.gcode.register_command(
            "MOTORLAB_STATUS",
            self.cmd_MOTORLAB_STATUS,
            desc="Show MotorLab status"
        )
        self.gcode.register_command(
            "MOTORLAB_ACCELEROMETER_QUERY",
            self.cmd_MOTORLAB_ACCELEROMETER_QUERY,
            desc="Forward to Klipper ACCELEROMETER_QUERY"
        )
        self.gcode.register_command(
            "MOTORLAB_MEASURE_AXES_NOISE",
            self.cmd_MOTORLAB_MEASURE_AXES_NOISE,
            desc="Forward to Klipper MEASURE_AXES_NOISE"
        )
        self.gcode.register_command(
            "MOTORLAB_ACCELEROMETER_MEASURE",
            self.cmd_MOTORLAB_ACCELEROMETER_MEASURE,
            desc="Forward to Klipper ACCELEROMETER_MEASURE"
        )
        self.gcode.register_command(
            "MOTORLAB_TEST_RESONANCES",
            self.cmd_MOTORLAB_TEST_RESONANCES,
            desc="Forward to Klipper TEST_RESONANCES"
        )
        self.gcode.register_command(
            "MOTORLAB_TEST_RESONANCES_SAVE",
            self.cmd_MOTORLAB_TEST_RESONANCES_SAVE,
            desc="Run TEST_RESONANCES and copy raw CSV files to MotorLab logs"
        )
        self.gcode.register_command(
            "MOTORLAB_SCORE_CSV",
            self.cmd_MOTORLAB_SCORE_CSV,
            desc="Score a CSV file and write a sorted summary"
        )
        self.gcode.register_command(
            "MOTORLAB_SHAPER_CALIBRATE",
            self.cmd_MOTORLAB_SHAPER_CALIBRATE,
            desc="Forward to Klipper SHAPER_CALIBRATE"
        )

        if self.mode in ("ptz", "full"):
            self.gcode.register_command(
                "MOTORLAB_TEST",
                self.cmd_MOTORLAB_TEST,
                desc="Run a MotorLab PTZ test"
            )

    def run_builtin_command(self, command):
        self.gcode.run_script_from_command(command)

    def get_stepper_name(self, axis):
        return axis

    def run_manual_stepper(self, stepper, move=None, speed=None, accel=None,
                           enable=None, sync=True):
        parts = ["MANUAL_STEPPER STEPPER=%s" % stepper]
        if enable is not None:
            parts.append("ENABLE=%d" % (1 if enable else 0))
        if move is not None:
            parts.append("MOVE=%.6f" % float(move))
        if speed is not None:
            parts.append("SPEED=%.6f" % float(speed))
        if accel is not None:
            parts.append("ACCEL=%.6f" % float(accel))
        parts.append("SYNC=%d" % (1 if sync else 0))
        self.gcode.run_script_from_command(" ".join(parts))

    def dwell(self, seconds):
        self.gcode.run_script_from_command("G4 P%d" % int(seconds * 1000.0))

    def _copy_recent_raw_data(self, started_at):
        copied = []
        for src in glob.glob("/tmp/raw_data*.csv"):
            try:
                if os.path.getmtime(src) < started_at:
                    continue
            except OSError:
                continue

            dst = os.path.join(self.log_path, os.path.basename(src))
            shutil.copy2(src, dst)
            copied.append(dst)
        return copied

    def _require_ptz_mode(self):
        if self.mode not in ("ptz", "full"):
            raise self.printer.command_error(
                "MOTORLAB_TEST is available only in ptz/full mode"
            )

    def _score_csv_path(self, path):
        scored = self.score.score_csv(path)
        if not scored:
            return None

        base = os.path.splitext(os.path.basename(path))[0]
        scored_path = os.path.join(self.log_path, "%s_scored.csv" % base)
        summary_path = os.path.join(self.log_path, "%s_summary.csv" % base)
        self.csv_exporter.export_run(scored_path, scored)
        self.csv_exporter.export_summary(summary_path, {
            "source_file": path,
            "best_score": scored[0]["score"],
            "best_test": scored[0].get("test"),
            "best_axis": scored[0].get("axis"),
            "rows_scored": len(scored),
        })
        return {
            "best": scored[0],
            "scored_path": scored_path,
            "summary_path": summary_path,
            "rows_scored": len(scored),
        }

    def cmd_MOTORLAB_STATUS(self, gcmd):
        gcmd.respond_info(
            "MotorLab mode=%s log_path=%s ptz=%s"
            % (
                self.mode,
                self.log_path,
                "yes" if self.mode in ("ptz", "full") else "no",
            )
        )

    def cmd_MOTORLAB_ACCELEROMETER_QUERY(self, gcmd):
        self.accelerometer.query()

    def cmd_MOTORLAB_MEASURE_AXES_NOISE(self, gcmd):
        self.accelerometer.measure_noise()

    def cmd_MOTORLAB_ACCELEROMETER_MEASURE(self, gcmd):
        self.accelerometer.measure()

    def cmd_MOTORLAB_TEST_RESONANCES(self, gcmd):
        axis = gcmd.get("AXIS", "X")
        output = gcmd.get("OUTPUT", None)
        self.accelerometer.test_resonances(axis, output=output)

    def cmd_MOTORLAB_TEST_RESONANCES_SAVE(self, gcmd):
        axis = gcmd.get("AXIS", "X")
        output = gcmd.get("OUTPUT", "raw_data")
        started_at = time.time()
        self.accelerometer.test_resonances(axis, output=output)
        copied = self._copy_recent_raw_data(started_at)
        if copied:
            gcmd.respond_info(
                "Copied %d CSV file(s) to %s"
                % (len(copied), self.log_path)
            )
        else:
            gcmd.respond_info(
                "No raw CSV files found in /tmp after TEST_RESONANCES"
            )

    def cmd_MOTORLAB_SCORE_CSV(self, gcmd):
        path = os.path.expanduser(gcmd.get("FILE"))
        if not os.path.exists(path):
            raise self.printer.command_error("CSV file not found: %s" % path)

        result = self._score_csv_path(path)
        if result is None:
            gcmd.respond_info("No scoreable rows found in %s" % path)
            return

        best = result["best"]
        gcmd.respond_info(
            "Best score=%.3f test=%s axis=%s scored=%s summary=%s"
            % (
                float(best["score"]),
                best.get("test"),
                best.get("axis"),
                result["scored_path"],
                result["summary_path"],
            )
        )

    def cmd_MOTORLAB_SHAPER_CALIBRATE(self, gcmd):
        axis = gcmd.get("AXIS", None)
        self.accelerometer.shaper_calibrate(axis=axis)

    def cmd_MOTORLAB_TEST(self, gcmd):
        self._require_ptz_mode()
        test_type = gcmd.get("TYPE").upper()
        axis = gcmd.get("AXIS", "pan")

        if test_type not in self.tests:
            raise self.printer.command_error(
                "Unknown MOTORLAB_TEST TYPE=%s" % test_type
            )

        test_cls = self.tests[test_type]
        test = test_cls(self, gcmd, axis)
        test.run()


def load_config(config):
    return MotorLab(config)
