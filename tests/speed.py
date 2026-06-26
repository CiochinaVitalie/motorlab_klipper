from .base import BaseMotorTest


class SpeedTest(BaseMotorTest):
    name = "SPEED"

    def execute(self):
        start_speed = self.gcmd.get_float("START", 10.0, above=0.0)
        stop_speed = self.gcmd.get_float("STOP", 400.0, above=0.0)
        step_speed = self.gcmd.get_float("STEP", 10.0, above=0.0)
        move_angle = self.gcmd.get_float("ANGLE", 90.0)
        repeat = self.gcmd.get_int("REPEAT", 3, minval=1)

        speed = start_speed
        while speed <= stop_speed + 1e-9:
            for n in range(repeat):
                self.safety_check()
                self.move_relative(move_angle, speed)
                self.lab.dwell(0.1)
                self.move_relative(-move_angle, speed)
                enc, err, mt, dt = self.read_common(target_deg=0.0)
                self.log.write({
                    "time": self.now(),
                    "axis": self.axis,
                    "test": self.name,
                    "speed_deg_s": speed,
                    "repeat": n,
                    "move_angle_deg": move_angle,
                    "encoder_deg": enc,
                    "error_deg": err,
                    "motor_temp_c": mt,
                    "driver_temp_c": dt,
                    "status": "OK",
                })
            speed += step_speed
