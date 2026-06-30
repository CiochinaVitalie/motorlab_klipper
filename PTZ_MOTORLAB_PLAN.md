# PTZ MotorLab Plan

This file describes how to extend MotorLab into a PTZ test framework where
Klipper orchestrates motion tests and collects telemetry from the motor driver,
accelerometer, and encoders.

## Goal

Use Klipper as the execution layer for PTZ motion tests and use MotorLab as the
test harness that:

- runs predefined motion patterns
- collects accelerometer data
- collects encoder feedback
- stores results in CSV
- evaluates candidate motor settings

## Modes

- `accelerometer_only`
  - Only ADXL345 and resonance-related commands are active.
  - This is the current trimmed runtime mode.

- `ptz`
  - Enables PTZ motion tests for `pan` and `tilt`.
  - Uses encoders and accelerometer feedback.
  - Stores test results in CSV.

- `full`
  - PTZ tests plus temperature, current, and any other available sensors.
  - Intended for final tuning and long-running validation.

## Roles

- Klipper
  - Executes G-code and manual stepper motion.
  - Provides native ADXL345 and resonance tools.

- MotorLab
  - Defines test scenarios.
  - Starts and stops runs.
  - Reads encoder and sensor data.
  - Writes structured CSV logs.
  - Computes a score for parameter selection.

- TMC2209
  - Drives the motors.
  - Provides motion control behavior but not final quality metrics.

- Encoder
  - Measures actual PTZ position.
  - Used for position error, backlash, and repeatability.

- ADXL345
  - Measures vibration and settling behavior.
  - Used for resonance and transient analysis.

## PTZ Test Set

### 1. Step Response

Short moves such as 5, 10, and 20 degrees.

Measures:

- time to reach target
- overshoot
- final position error
- vibration after stop

### 2. Speed Sweep

Fixed angle, multiple speeds.

Measures:

- maximum usable speed
- motion stability
- position error at each speed

### 3. Acceleration Sweep

Fixed speed, multiple acceleration values.

Measures:

- best usable acceleration
- vibration growth
- settling behavior

### 4. Repeatability

Repeated identical moves back and forth.

Measures:

- spread of final position
- drift over time
- consistency of motion

### 5. Backlash

Approach the same target from opposite directions.

Measures:

- directional offset
- mechanical play
- return error

### 6. Settling

Observe the axis after each move until vibration decays.

Measures:

- settling time
- peak vibration
- RMS vibration

### 7. Endurance

Long series of moves under load.

Measures:

- temperature rise
- drift
- degradation over time

## CSV Fields

Recommended minimum fields:

- `timestamp`
- `axis`
- `test_name`
- `target_angle_deg`
- `actual_angle_deg`
- `position_error_deg`
- `speed_deg_s`
- `accel_deg_s2`
- `settle_time_ms`
- `peak_accel`
- `rms_accel`
- `motor_temp_c`
- `driver_temp_c`
- `status`

Optional fields when available:

- `pan_encoder_deg`
- `tilt_encoder_deg`
- `current_a`
- raw accelerometer file path

## Parameter Selection

Use a score to compare candidate settings.

Suggested penalties:

- large position error
- large settling time
- high vibration
- high temperature
- backlash
- repeated instability

Example selection rule:

1. Reject any run with unacceptable error, overshoot, or temperature.
2. Among the remaining runs, prefer the lowest vibration.
3. If vibration is similar, prefer faster settling time.
4. If still similar, prefer the faster motion settings.

## Klipper Flow

1. Klipper receives a MotorLab test command.
2. MotorLab sends motion commands to `manual_stepper`.
3. ADXL345 collects vibration data through native Klipper support.
4. Encoders report actual position.
5. MotorLab writes one CSV row per test event.
6. A post-processing step selects the best parameter set.

## Suggested Commands

- `MOTORLAB_ACCELEROMETER_QUERY`
- `MOTORLAB_MEASURE_AXES_NOISE`
- `MOTORLAB_ACCELEROMETER_MEASURE`
- `MOTORLAB_TEST_RESONANCES`
- `MOTORLAB_TEST_RESONANCES_SAVE`
- `MOTORLAB_SHAPER_CALIBRATE`

For PTZ mode later:

- `MOTORLAB_TEST TYPE=STEP_RESPONSE AXIS=pan`
- `MOTORLAB_TEST TYPE=SPEED_SWEEP AXIS=pan`
- `MOTORLAB_TEST TYPE=ACCEL_SWEEP AXIS=tilt`
- `MOTORLAB_TEST TYPE=REPEATABILITY AXIS=pan`
- `MOTORLAB_TEST TYPE=BACKLASH AXIS=tilt`
- `MOTORLAB_TEST TYPE=ENDURANCE AXIS=pan`

## Implementation Notes

- Keep `accelerometer_only` as the default mode.
- Add a config flag to enable `ptz` and `full`.
- Restore motor test classes behind that mode switch.
- Keep the ADXL345 wrapper active in all modes.
- Store saved resonance CSV files in the MotorLab log directory.

