# MotorLab for Klipper

MotorLab is an experimental Klipper module. It can run in an accelerometer-only
mode or a PTZ test mode.

## Modes

- `accelerometer_only`
  - Only ADXL345 and resonance-related commands are active.
  - This is the default mode.

- `ptz`
  - Enables PTZ motion tests for `pan` and `tilt`.
  - Uses encoder and temperature helpers.

- `full`
  - PTZ tests plus any extra sensors you wire in later.

## Encoder UART Format

The encoder input is expected as one ASCII line per sample:

```text
ENC,pan,123.45
ENC,tilt,-12.80
```

Rules:
- prefix: `ENC`
- field 2: axis name, usually `pan` or `tilt`
- field 3: angle in degrees
- line ending: `\n`
- extra fields are ignored

Recommended rate:
- start with `50 Hz`
- use `100 Hz` only if you need tighter settling analysis

## Install

Copy the `motorlab/` folder into:

```text
~/klipper/klippy/extras/motorlab/
```

Then add the configuration from `printer.cfg.example` to your `printer.cfg`
and restart Klipper.

## Commands

Accelerometer and resonance wrappers:

```gcode
MOTORLAB_ACCELEROMETER_QUERY
MOTORLAB_MEASURE_AXES_NOISE
MOTORLAB_ACCELEROMETER_MEASURE
MOTORLAB_TEST_RESONANCES AXIS=X OUTPUT=raw_data
MOTORLAB_TEST_RESONANCES_SAVE AXIS=X OUTPUT=raw_data
MOTORLAB_SHAPER_CALIBRATE AXIS=X
```

CSV scoring:

```gcode
MOTORLAB_SCORE_CSV FILE=/path/to/run.csv
```

This command scores each row in the CSV, writes a sorted `*_scored.csv` file in
`log_path`, and writes a small `*_summary.csv` file with the best run.

PTZ tests available in `mode: ptz` or `mode: full`:

```gcode
MOTORLAB_TEST TYPE=PTZ_STEP_RESPONSE AXIS=pan
MOTORLAB_TEST TYPE=PTZ_SPEED_SWEEP AXIS=pan
MOTORLAB_TEST TYPE=PTZ_ACCEL_SWEEP AXIS=tilt
MOTORLAB_TEST TYPE=PTZ_SETTLING AXIS=pan
MOTORLAB_TEST TYPE=PTZ_BACKLASH AXIS=tilt
MOTORLAB_TEST TYPE=PTZ_ENDURANCE AXIS=pan
```

Implemented PTZ tests:

- `PTZ_STEP_RESPONSE`
  - moves to a target angle, waits for encoder settle, returns home, logs CSV
- `PTZ_SPEED_SWEEP`
  - sweeps through speeds for a fixed angle and logs settle metrics
- `PTZ_ACCEL_SWEEP`
  - sweeps through acceleration values for a fixed angle and logs settle metrics
- `PTZ_BACKLASH`
  - approaches the same target from opposite directions and compares error
- `PTZ_SETTLING`
  - measures settling time and residual error after a move
- `PTZ_ENDURANCE`
  - repeats a motion cycle and logs periodically for long runs

After each PTZ test finishes, MotorLab automatically scores the generated CSV
and writes `*_scored.csv` plus `*_summary.csv` into `log_path`.

`MOTORLAB_TEST_RESONANCES_SAVE` runs the native Klipper resonance test and then
copies any newly created `/tmp/raw_data*.csv` files into the MotorLab log
directory.

## Notes

All PTZ test classes are implemented. The main missing piece is the actual
sensor implementation behind `encoder.py` and `temperature.py`, which still need
to be wired to real hardware for production use.
