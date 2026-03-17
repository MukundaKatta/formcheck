# FormCheck - AI Personal Trainer

FormCheck is an AI-powered personal trainer that uses pose estimation and form
analysis to provide real-time exercise correction feedback.

## Features

- **Pose Detection**: CNN-based detector extracting 17 body keypoints from video
  frames.
- **Form Analysis**: Computes joint angles and compares them against reference
  form for 20+ exercises.
- **Correction Engine**: Identifies specific corrections and provides actionable
  cues.
- **Rep Counting**: Automatically counts repetitions by detecting joint-angle
  cycles.
- **Workout Tracking**: Logs sets, reps, and per-rep form scores.
- **Reports**: Generates rich console reports summarising workout quality.

## Supported Exercises

Squat, Front Squat, Deadlift, Romanian Deadlift, Bench Press, Overhead Press,
Barbell Row, Push-up, Pull-up, Dip, Plank, Side Plank, Lunge, Bulgarian Split
Squat, Hip Thrust, Bicep Curl, Tricep Extension, Lateral Raise, Face Pull,
Calf Raise, Leg Press, and Leg Curl.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Analyse a workout video
formcheck analyse --video workout.mp4 --exercise squat

# Run a simulated workout and generate a report
formcheck simulate --exercise deadlift --reps 8

# List supported exercises
formcheck exercises
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Architecture

```
src/formcheck/
  cli.py            - Click CLI entry-point
  models.py         - Pydantic data models
  simulator.py      - Synthetic pose data generator
  report.py         - Rich console reporter
  pose/
    detector.py     - PoseDetector CNN (17 keypoints)
    analyzer.py     - FormAnalyzer (joint angles & comparison)
    corrector.py    - FormCorrector (correction identification)
  exercises/
    database.py     - ExerciseDatabase (20+ exercises w/ angles)
    rep_counter.py  - RepCounter (cycle detection)
    workout.py      - WorkoutTracker (sets/reps/scores)
```

## License

MIT
