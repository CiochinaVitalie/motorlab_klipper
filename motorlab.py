# MotorLab for Klipper
# Copy folder to: klippy/extras/motorlab/
#
# Klipper config section:
# [motorlab]

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
            "MOTORLAB_SHAPER_CALIBRATE",
            self.cmd_MOTORLAB_SHAPER_CALIBRATE,
            desc="Forward to Klipper SHAPER_CALIBRATE"
        )

    def run_builtin_command(self, command):
        self.gcode.run_script_from_command(command)

    def cmd_MOTORLAB_STATUS(self, gcmd):
        gcmd.respond_info(
            "MotorLab accelerometer wrappers enabled"
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

    def cmd_MOTORLAB_SHAPER_CALIBRATE(self, gcmd):
        axis = gcmd.get("AXIS", None)
        self.accelerometer.shaper_calibrate(axis=axis)


def load_config(config):
    return MotorLab(config)
