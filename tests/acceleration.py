from .base import BaseMotorTest


class AccelerationTest(BaseMotorTest):
    name = "ACCELERATION"

    def execute(self):
        start_accel = self.gcmd.get_float("START", 100.0, above=0.0)
        stop_accel = self.gcmd.get_float("STOP", 3000.0, above=0.0)
        step_accel = self.gcmd.get_float("STEP", 100.0, above=0.0)
        speed = self.gcmd.get_float("SPEED", 80.0, above=0.0)
        move_angle = self.gcmd.get_float("ANGLE", 90.0)
        repeat = self.gcmd.get_int("REPEAT", 3, minval=1)

        accel = start_accel
        while accel <= stop_accel + 1e-9:
            for n in range(repeat):
                self.safety_check()
                self.move_relative(move_angle, speed, accel)
                self.lab.dwell(0.1)
                self.move_relative(-move_angle, speed, accel)
                enc, err, mt, dt = self.read_common(target_deg=0.0)
                self.log.write({
                    "time": self.now(),
                    "axis": self.axis,
                    "test": self.name,
                    "accel_deg_s2": accel,
                    "speed_deg_s": speed,
                    "repeat": n,
                    "move_angle_deg": move_angle,
                    "encoder_deg": enc,
                    "error_deg": err,
                    "motor_temp_c": mt,
                    "driver_temp_c": dt,
                    "status": "OK",
                })
            accel += step_accel
