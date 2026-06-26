import time


class BaseMotorTest:
    name = "BASE"

    def __init__(self, lab, gcmd, axis):
        self.lab = lab
        self.gcmd = gcmd
        self.axis = axis
        self.stepper = lab.get_stepper_name(axis)
        self.log = None

    def cfg(self, section_name):
        try:
            return self.lab.printer.lookup_object("configfile").get_status(
                self.lab.printer.get_reactor().monotonic()
            )
        except Exception:
            return None

    def now(self):
        return time.time()

    def setup(self):
        self.log = self.lab.logger.open_csv(self.name, self.axis)
        self.lab.run_manual_stepper(self.stepper, enable=True)

    def finish(self):
        if self.log:
            self.log.close()
        self.gcmd.respond_info("%s test done for axis=%s" % (self.name, self.axis))

    def run(self):
        self.setup()
        try:
            self.execute()
        finally:
            self.finish()

    def move_relative(self, angle_deg, speed, accel=None):
        self.lab.run_manual_stepper(
            self.stepper,
            move=angle_deg,
            speed=speed,
            accel=accel,
            sync=True
        )

    def read_common(self, target_deg=None):
        enc = self.lab.encoder.read_angle_deg(self.axis)
        err = None
        if enc is not None and target_deg is not None:
            err = enc - target_deg
        motor_temp = self.lab.temperature.motor_temp(self.axis)
        driver_temp = self.lab.temperature.driver_temp(self.axis)
        return enc, err, motor_temp, driver_temp

    def safety_check(self):
        ok, reason = self.lab.temperature.check_limits(self.axis)
        if not ok:
            raise self.lab.printer.command_error("MotorLab stopped: %s" % reason)

    def execute(self):
        raise NotImplementedError
