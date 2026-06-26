from .base import BaseMotorTest


class BacklashTest(BaseMotorTest):
    name = "BACKLASH"

    def execute(self):
        cycles = self.gcmd.get_int("CYCLES", 50, minval=1)
        move_angle = self.gcmd.get_float("ANGLE", 10.0)
        speed = self.gcmd.get_float("SPEED", 20.0, above=0.0)

        for i in range(cycles):
            self.safety_check()

            self.move_relative(move_angle, speed)
            self.lab.dwell(0.1)
            enc_plus, _, mt, dt = self.read_common()

            self.move_relative(-move_angle, speed)
            self.lab.dwell(0.1)
            enc_zero, err_zero, mt, dt = self.read_common(target_deg=0.0)

            self.log.write({
                "time": self.now(),
                "axis": self.axis,
                "test": self.name,
                "cycle": i,
                "move_angle_deg": move_angle,
                "speed_deg_s": speed,
                "encoder_after_plus_deg": enc_plus,
                "encoder_after_return_deg": enc_zero,
                "return_error_deg": err_zero,
                "motor_temp_c": mt,
                "driver_temp_c": dt,
                "status": "OK",
            })
