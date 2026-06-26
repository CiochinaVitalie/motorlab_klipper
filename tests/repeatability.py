from .base import BaseMotorTest


class RepeatabilityTest(BaseMotorTest):
    name = "REPEATABILITY"

    def execute(self):
        cycles = self.gcmd.get_int("CYCLES", 100, minval=1)
        move_angle = self.gcmd.get_float("ANGLE", 90.0)
        speed = self.gcmd.get_float("SPEED", 80.0, above=0.0)

        for i in range(cycles):
            self.safety_check()
            self.move_relative(move_angle, speed)
            self.lab.dwell(0.05)
            self.move_relative(-move_angle, speed)
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
