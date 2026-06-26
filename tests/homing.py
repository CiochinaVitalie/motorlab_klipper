from .base import BaseMotorTest


class HomingTest(BaseMotorTest):
    name = "HOMING"

    def execute(self):
        cycles = self.gcmd.get_int("CYCLES", 100, minval=1)
        move_away = self.gcmd.get_float("AWAY", 30.0)
        speed = self.gcmd.get_float("SPEED", 40.0, above=0.0)

        for i in range(cycles):
            self.safety_check()

            self.move_relative(move_away, speed)

            # For real homing, replace this with a configured MANUAL_STEPPER
            # homing command if your axis has an endstop.
            # Example manually:
            # MANUAL_STEPPER STEPPER=pan MOVE=-100 SPEED=20 STOP_ON_ENDSTOP=1
            self.lab.run_manual_stepper(
                self.stepper,
                move=-abs(move_away) * 2.0,
                speed=speed,
                sync=True
            )

            enc, err, mt, dt = self.read_common(target_deg=0.0)
            self.log.write({
                "time": self.now(),
                "axis": self.axis,
                "test": self.name,
                "cycle": i,
                "move_away_deg": move_away,
                "speed_deg_s": speed,
                "encoder_deg": enc,
                "home_error_deg": err,
                "motor_temp_c": mt,
                "driver_temp_c": dt,
                "status": "OK",
            })
