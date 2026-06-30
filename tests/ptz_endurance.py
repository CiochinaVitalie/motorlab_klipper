from .base import BaseMotorTest


class PTZEnduranceTest(BaseMotorTest):
    name = "PTZ_ENDURANCE"

    def log_cycle(self, cycle_index, angle_deg, speed, accel, motor_temp, driver_temp,
                  settle_forward, settle_return, start_enc):
        self.log_row({
            "time": self.now(),
            "axis": self.axis,
            "test": self.name,
            "cycle": cycle_index,
            "target_angle_deg": angle_deg,
            "speed_deg_s": speed,
            "accel_deg_s2": accel,
            "start_encoder_deg": start_enc,
            "forward_settle_time_ms": settle_forward["settle_time_ms"],
            "forward_peak_error_deg": settle_forward["peak_error_deg"],
            "forward_final_encoder_deg": settle_forward["final_encoder_deg"],
            "forward_final_error_deg": settle_forward["final_error_deg"],
            "return_settle_time_ms": settle_return["settle_time_ms"],
            "return_peak_error_deg": settle_return["peak_error_deg"],
            "return_final_encoder_deg": settle_return["final_encoder_deg"],
            "return_final_error_deg": settle_return["final_error_deg"],
            "motor_temp_c": motor_temp,
            "driver_temp_c": driver_temp,
            "status": "OK" if settle_forward["final_error_deg"] is not None else "NO_ENCODER",
        })

    def execute(self):
        cycles = self.gcmd.get_int("CYCLES", 1000, minval=1)
        angle_deg = self.gcmd.get_float("ANGLE", 10.0)
        speed = self.gcmd.get_float("SPEED", 20.0, above=0.0)
        accel_raw = self.gcmd.get("ACCEL", None)
        accel = float(accel_raw) if accel_raw is not None else None
        log_every = self.gcmd.get_int("LOG_EVERY", 10, minval=1)
        settle_deg = self.gcmd.get_float("SETTLE_DEG", 0.1, above=0.0)
        settle_timeout_s = self.gcmd.get_float("TIMEOUT", 2.0, above=0.0)
        sample_interval_s = self.gcmd.get_float("SAMPLE", 0.05, above=0.0)

        for i in range(cycles):
            self.safety_check()
            start_enc, _, motor_temp, driver_temp = self.read_common(target_deg=0.0)

            self.move_relative(angle_deg, speed, accel=accel)
            settle_forward = self.measure_settle(
                target_deg=angle_deg,
                tolerance_deg=settle_deg,
                timeout_s=settle_timeout_s,
                sample_interval_s=sample_interval_s,
            )
            self.move_relative(-angle_deg, speed, accel=accel)
            settle_return = self.measure_settle(
                target_deg=0.0,
                tolerance_deg=settle_deg,
                timeout_s=settle_timeout_s,
                sample_interval_s=sample_interval_s,
            )

            if i % log_every == 0 or i == cycles - 1:
                self.log_cycle(
                    cycle_index=i,
                    angle_deg=angle_deg,
                    speed=speed,
                    accel=accel,
                    motor_temp=motor_temp,
                    driver_temp=driver_temp,
                    settle_forward=settle_forward,
                    settle_return=settle_return,
                    start_enc=start_enc,
                )
