import threading

try:
    import serial
except Exception:  # pragma: no cover - fallback for environments without pyserial
    serial = None


class MotorLabEncoder:
    """
    UART-backed encoder interface.

    Expected input format, one line per sample:

        ENC,<axis>,<angle_deg>\n
    Examples:

        ENC,pan,123.45
        ENC,tilt,-12.80

    Optional trailing fields are ignored by the parser.
    """

    def __init__(self, config):
        self.enabled = False
        self.tolerance = 0.1
        self.device = None
        self.baudrate = 115200
        self.timeout = 0.1
        self.prefix = "ENC"

        self._serial = None
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._latest = {}
        self._last_raw = {}

        try:
            enc_cfg = config.getsection("motorlab_encoder")
            self.enabled = enc_cfg.getboolean("enabled", False)
            self.tolerance = enc_cfg.getfloat("position_tolerance_deg", 0.1)
            self.device = enc_cfg.get("device", None)
            self.baudrate = enc_cfg.getint("baudrate", 115200)
            self.timeout = enc_cfg.getfloat("timeout", 0.1)
            self.prefix = enc_cfg.get("prefix", "ENC").strip()
        except Exception:
            pass

        if self.enabled:
            self._open()

    def _open(self):
        if serial is None:
            raise RuntimeError(
                "pyserial is required for motorlab_encoder, but it is not available"
            )
        if not self.device:
            raise RuntimeError("motorlab_encoder.enabled=true requires motorlab_encoder.device")

        self._serial = serial.Serial(
            self.device,
            baudrate=self.baudrate,
            timeout=self.timeout,
        )
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def close(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass

    def _reader_loop(self):
        while not self._stop_event.is_set():
            try:
                raw = self._serial.readline()
            except Exception:
                break

            if not raw:
                continue

            try:
                line = raw.decode("ascii", errors="ignore").strip()
            except Exception:
                continue

            parsed = self._parse_line(line)
            if parsed is None:
                continue

            axis, angle_deg, payload = parsed
            with self._lock:
                self._latest[axis] = angle_deg
                self._last_raw[axis] = payload

    def _parse_line(self, line):
        if not line:
            return None

        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 3:
            return None
        if parts[0] != self.prefix:
            return None

        axis = parts[1].lower()
        try:
            angle_deg = float(parts[2])
        except ValueError:
            return None

        payload = {
            "raw": line,
            "axis": axis,
            "angle_deg": angle_deg,
        }
        if len(parts) > 3:
            payload["extra"] = parts[3:]
        return axis, angle_deg, payload

    def read_angle_deg(self, axis):
        if not self.enabled:
            return None
        with self._lock:
            return self._latest.get(axis)

    def last_payload(self, axis):
        with self._lock:
            return self._last_raw.get(axis)

    def position_error_deg(self, axis, target_deg):
        angle = self.read_angle_deg(axis)
        if angle is None:
            return None
        return angle - target_deg
