import glob
import os
import shutil
import time

from .sensors.adxl345 import KlipperADXL345

# Motor test code is kept in the repository for reference, but it is not
# registered in the active runtime path for the accelerometer-only mode.
# from .logger import MotorLabLogger
# from .encoder import MotorLabEncoder
# from .sensors.temperature import TemperatureMonitor
# from .tests.speed import SpeedTest
# from .tests.acceleration import AccelerationTest
# from .tests.repeatability import RepeatabilityTest
# from .tests.backlash import BacklashTest
# from .tests.endurance import EnduranceTest
# from .tests.homing import HomingTest


class MotorLab:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object("gcode")
        self.log_path = os.path.expanduser(
            config.get("log_path", "~/printer_data/logs/motorlab")
        )
        os.makedirs(self.log_path, exist_ok=True)

        self.accelerometer = KlipperADXL345(self)

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
            "MOTORLAB_SHAPER_CALIBRATE",
            self.cmd_MOTORLAB_SHAPER_CALIBRATE,
            desc="Forward to Klipper SHAPER_CALIBRATE"
        )

    def run_builtin_command(self, command):
        self.gcode.run_script_from_command(command)

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

    def cmd_MOTORLAB_STATUS(self, gcmd):
        gcmd.respond_info(
            "MotorLab accelerometer wrappers enabled log_path=%s"
            % self.log_path
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

    def cmd_MOTORLAB_SHAPER_CALIBRATE(self, gcmd):
        axis = gcmd.get("AXIS", None)
        self.accelerometer.shaper_calibrate(axis=axis)


def load_config(config):
    return MotorLab(config)
