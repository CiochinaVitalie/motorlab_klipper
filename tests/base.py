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
        if self.lab.logger is not None:
            self.log = self.lab.logger.open_csv(self.name, self.axis)
        self.lab.run_manual_stepper(self.stepper, enable=True)

    def finish(self):
        score_msg = ""
        if self.log:
            self.log.close()
            if self.lab.mode in ("ptz", "full"):
                result = self.lab._score_csv_path(self.log.path)
                if result is not None:
                    best = result["best"]
                    score_msg = (
                        " best_score=%.3f scored=%s summary=%s"
                        % (
                            float(best["score"]),
                            result["scored_path"],
                            result["summary_path"],
                        )
                    )
        self.gcmd.respond_info(
            "%s test done for axis=%s%s" % (self.name, self.axis, score_msg)
        )

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

    def read_encoder(self):
        if self.lab.encoder is None:
            return None
        return self.lab.encoder.read_angle_deg(self.axis)

    def read_temperatures(self):
        if self.lab.temperature is None:
            return None, None
        motor_temp = self.lab.temperature.motor_temp(self.axis)
        driver_temp = self.lab.temperature.driver_temp(self.axis)
        return motor_temp, driver_temp

    def read_common(self, target_deg=None):
        enc = self.read_encoder()
        err = None
        if enc is not None and target_deg is not None:
            err = enc - target_deg
        motor_temp, driver_temp = self.read_temperatures()
        return enc, err, motor_temp, driver_temp

    def safety_check(self):
        if self.lab.temperature is None:
            return
        ok, reason = self.lab.temperature.check_limits(self.axis)
        if not ok:
            raise self.lab.printer.command_error("MotorLab stopped: %s" % reason)

    def log_row(self, row):
        if self.log is not None:
            self.log.write(row)

    def measure_settle(self, target_deg, tolerance_deg=0.1, timeout_s=2.0,
                       sample_interval_s=0.05, stable_samples=4):
        started = self.now()
        peak_error = None
        stable_count = 0
        last_enc = None
        sample_count = 0
        settle_time_ms = None

        while (self.now() - started) < timeout_s:
            self.safety_check()
            enc = self.read_encoder()
            sample_count += 1
            if enc is not None:
                err = enc - target_deg
                abs_err = abs(err)
                if peak_error is None or abs_err > peak_error:
                    peak_error = abs_err
                if abs_err <= tolerance_deg:
                    if last_enc is not None and abs(enc - last_enc) <= tolerance_deg:
                        stable_count += 1
                    else:
                        stable_count = 1
                else:
                    stable_count = 0
                last_enc = enc
                if stable_count >= stable_samples:
                    settle_time_ms = (self.now() - started) * 1000.0
                    break
            self.lab.dwell(sample_interval_s)

        final_enc = self.read_encoder()
        final_error = None
        if final_enc is not None:
            final_error = final_enc - target_deg

        return {
            "settle_time_ms": settle_time_ms,
            "peak_error_deg": peak_error,
            "final_encoder_deg": final_enc,
            "final_error_deg": final_error,
            "sample_count": sample_count,
        }

    def execute(self):
        raise NotImplementedError
