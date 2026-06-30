class CameraAnalyzer:
    """Analyze PTZ camera frames or tracking output if camera feedback is used."""

    def capture_frame(self):
        raise NotImplementedError

    def measure_target_offset(self, frame):
        raise NotImplementedError

    def compare_before_after(self, before_frame, after_frame):
        raise NotImplementedError
