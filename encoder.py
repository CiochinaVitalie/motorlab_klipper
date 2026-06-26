class MotorLabEncoder:
    """
    Placeholder encoder interface.

    Replace read_angle_deg() with UART/CAN/SPI/I2C code for your real encoder.
    If enabled=false, tests still run, but encoder fields are reported as None.
    """

    def __init__(self, config):
        self.enabled = False
        self.tolerance = 0.1

        try:
            enc_cfg = config.getsection("motorlab_encoder")
            self.enabled = enc_cfg.getboolean("enabled", False)
            self.tolerance = enc_cfg.getfloat("position_tolerance_deg", 0.1)
        except Exception:
            pass

    def read_angle_deg(self, axis):
        if not self.enabled:
            return None
        # TODO: implement real hardware read here.
        return None

    def position_error_deg(self, axis, target_deg):
        angle = self.read_angle_deg(axis)
        if angle is None:
            return None
        return angle - target_deg
