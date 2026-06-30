from .base import BaseMotorTest


class PTZBacklashTest(BaseMotorTest):
    name = "PTZ_BACKLASH"

    def measure_directional_error(self, approach_deg, speed, accel=None,
                                  settle_deg=0.1, settle_timeout_s=2.0,
                                  sample_interval_s=0.05):
        self.move_relative(approach_deg, speed, accel=accel)
        forward = self.measure_settle(
            target_deg=approach_deg,
            tolerance_deg=settle_deg,
            timeout_s=settle_timeout_s,
            sample_interval_s=sample_interval_s,
        )
        self.move_relative(-approach_deg, speed, accel=accel)
        return_home = self.measure_settle(
            target_deg=0.0,
            tolerance_deg=settle_deg,
            timeout_s=settle_timeout_s,
            sample_interval_s=sample_interval_s,
        )
        return forward, return_home

    def execute(self):
        approach_deg = self.gcmd.get_float("ANGLE", 5.0)
        speed = self.gcmd.get_float("SPEED", 10.0, above=0.0)
        accel_raw = self.gcmd.get("ACCEL", None)
        accel = float(accel_raw) if accel_raw is not None else None
        repeats = self.gcmd.get_int("REPEAT", 5, minval=1)
        settle_deg = self.gcmd.get_float("SETTLE_DEG", 0.1, above=0.0)
        settle_timeout_s = self.gcmd.get_float("TIMEOUT", 2.0, above=0.0)
        sample_interval_s = self.gcmd.get_float("SAMPLE", 0.05, above=0.0)

        for i in range(repeats):
            self.safety_check()
            start_enc, _, motor_temp, driver_temp = self.read_common(target_deg=0.0)

            forward, return_home = self.measure_directional_error(
                approach_deg=approach_deg,
                speed=speed,
                accel=accel,
                settle_deg=settle_deg,
                settle_timeout_s=settle_timeout_s,
                sample_interval_s=sample_interval_s,
            )

            self.move_relative(-approach_deg, speed, accel=accel)
            reverse = self.measure_settle(
                target_deg=-approach_deg,
                tolerance_deg=settle_deg,
                timeout_s=settle_timeout_s,
                sample_interval_s=sample_interval_s,
            )
            self.move_relative(approach_deg, speed, accel=accel)
            reverse_return = self.measure_settle(
                target_deg=0.0,
                tolerance_deg=settle_deg,
                timeout_s=settle_timeout_s,
                sample_interval_s=sample_interval_s,
            )

            self.log_row({
                "time": self.now(),
                "axis": self.axis,
                "test": self.name,
                "repeat": i,
                "approach_angle_deg": approach_deg,
                "speed_deg_s": speed,
                "accel_deg_s2": accel,
                "start_encoder_deg": start_enc,
                "forward_final_error_deg": forward["final_error_deg"],
                "forward_peak_error_deg": forward["peak_error_deg"],
                "return_final_error_deg": return_home["final_error_deg"],
                "reverse_final_error_deg": reverse["final_error_deg"],
                "reverse_peak_error_deg": reverse["peak_error_deg"],
                "reverse_return_final_error_deg": reverse_return["final_error_deg"],
                "motor_temp_c": motor_temp,
                "driver_temp_c": driver_temp,
                "status": "OK" if forward["final_error_deg"] is not None else "NO_ENCODER",
            })
