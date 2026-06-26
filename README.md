# MotorLab for Klipper

MotorLab is an experimental Klipper module. In the current trimmed mode it only
forwards ADXL345 and resonance-related commands to Klipper's built-in support.

## Install

Copy the `motorlab/` folder into:

```text
~/klipper/klippy/extras/motorlab/
```

Then add the accelerometer configuration from `printer.cfg.example` to your
`printer.cfg` and restart Klipper.

## Commands

```gcode
MOTORLAB_ACCELEROMETER_QUERY
MOTORLAB_MEASURE_AXES_NOISE
MOTORLAB_ACCELEROMETER_MEASURE
MOTORLAB_TEST_RESONANCES AXIS=X OUTPUT=raw_data
MOTORLAB_TEST_RESONANCES_SAVE AXIS=X OUTPUT=raw_data
MOTORLAB_SHAPER_CALIBRATE AXIS=X
```

`MOTORLAB_TEST_RESONANCES_SAVE` runs the native Klipper resonance test and then
copies any newly created `/tmp/raw_data*.csv` files into the MotorLab log
directory.

## Notes

This build is accelerometer-only. The motor test framework, encoder hooks, and
temperature hooks are kept in the repository as commented or unused code for
reference, but they are not part of the active runtime path.
