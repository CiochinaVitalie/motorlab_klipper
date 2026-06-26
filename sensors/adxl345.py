class KlipperADXL345:
    """
    Thin wrapper around Klipper's built-in accelerometer and resonance tools.

    MotorLab does not read the sensor directly. Instead, it forwards commands
    to Klipper's native ADXL345 support and resonance tester.
    """

    def __init__(self, lab):
        self.lab = lab

    def _run(self, command):
        self.lab.gcode.run_script_from_command(command)

    def query(self):
        self._run("ACCELEROMETER_QUERY")

    def measure_noise(self):
        self._run("MEASURE_AXES_NOISE")

    def measure(self):
        self._run("ACCELEROMETER_MEASURE")

    def test_resonances(self, axis, output=None):
        parts = ["TEST_RESONANCES AXIS=%s" % axis]
        if output:
            parts.append("OUTPUT=%s" % output)
        self._run(" ".join(parts))

    def shaper_calibrate(self, axis=None):
        parts = ["SHAPER_CALIBRATE"]
        if axis:
            parts.append("AXIS=%s" % axis)
        self._run(" ".join(parts))
