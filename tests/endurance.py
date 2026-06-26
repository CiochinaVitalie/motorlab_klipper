from .base import BaseMotorTest


class EnduranceTest(BaseMotorTest):
    name = "ENDURANCE"

    def execute(self):
        cycles = self.gcmd.get_int("CYCLES", 1000, minval=1)
        move_angle = self.gcmd.get_float("ANGLE", 90.0)
        speed = self.gcmd.get_float("SPEED", 80.0, above=0.0)
        log_every = self.gcmd.get_int("LOG_EVERY", 10, minval=1)

        for i in range(cycles):
            self.safety_check()
            self.move_relative(move_angle, speed)
            self.move_relative(-move_angle, speed)

            if i % log_every == 0 or i == cycles - 1:
                enc, err, mt, dt = self.read_common(target_deg=0.0)
                self.log.write({
                    "time": self.now(),
                    "axis": self.axis,
                    "test": self.name,
                    "cycle": i,
                    "move_angle_deg": move_angle,
                    "speed_deg_s": speed,
                    "encoder_deg": enc,
                    "error_deg": err,
                    "motor_temp_c": mt,
                    "driver_temp_c": dt,
                    "status": "OK",
                })
