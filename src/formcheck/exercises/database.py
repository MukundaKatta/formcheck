"""ExerciseDatabase - catalogue of 20+ exercises with correct joint angles."""

from __future__ import annotations

from formcheck.models import Exercise

# ---------------------------------------------------------------------------
# Exercise definitions
#
# correct_angles maps joint name -> (ideal_angle_degrees, tolerance_degrees).
# rep_angle_range is (bottom_angle, top_angle) for the rep_joint.
# ---------------------------------------------------------------------------

_EXERCISES: list[Exercise] = [
    # 1. Squat
    Exercise(
        name="Squat",
        slug="squat",
        category="lower",
        primary_muscles=["quadriceps", "glutes", "hamstrings"],
        joints_to_track=["left_knee", "right_knee", "left_hip", "right_hip"],
        correct_angles={
            "left_knee": (90.0, 15.0),
            "right_knee": (90.0, 15.0),
            "left_hip": (90.0, 15.0),
            "right_hip": (90.0, 15.0),
        },
        rep_joint="left_knee",
        rep_angle_range=(80.0, 170.0),
        cues={
            "left_knee": "Push knees out over toes; aim for 90-degree bend at the bottom.",
            "right_knee": "Push knees out over toes; aim for 90-degree bend at the bottom.",
            "left_hip": "Sit hips back and down; keep chest up.",
            "right_hip": "Sit hips back and down; keep chest up.",
        },
    ),
    # 2. Front Squat
    Exercise(
        name="Front Squat",
        slug="front_squat",
        category="lower",
        primary_muscles=["quadriceps", "glutes", "core"],
        joints_to_track=["left_knee", "right_knee", "left_hip", "right_hip", "left_elbow", "right_elbow"],
        correct_angles={
            "left_knee": (85.0, 15.0),
            "right_knee": (85.0, 15.0),
            "left_hip": (85.0, 15.0),
            "right_hip": (85.0, 15.0),
            "left_elbow": (90.0, 20.0),
            "right_elbow": (90.0, 20.0),
        },
        rep_joint="left_knee",
        rep_angle_range=(75.0, 170.0),
        cues={
            "left_knee": "Keep knees tracking over toes; sit deep.",
            "right_knee": "Keep knees tracking over toes; sit deep.",
            "left_elbow": "Keep elbows high to hold the bar in the front rack.",
            "right_elbow": "Keep elbows high to hold the bar in the front rack.",
        },
    ),
    # 3. Deadlift
    Exercise(
        name="Deadlift",
        slug="deadlift",
        category="lower",
        primary_muscles=["hamstrings", "glutes", "erector spinae"],
        joints_to_track=["left_hip", "right_hip", "left_knee", "right_knee"],
        correct_angles={
            "left_hip": (170.0, 15.0),
            "right_hip": (170.0, 15.0),
            "left_knee": (170.0, 15.0),
            "right_knee": (170.0, 15.0),
        },
        rep_joint="left_hip",
        rep_angle_range=(90.0, 170.0),
        cues={
            "left_hip": "Drive hips forward to lockout; squeeze glutes.",
            "right_hip": "Drive hips forward to lockout; squeeze glutes.",
            "left_knee": "Keep a slight bend; don't hyper-extend.",
            "right_knee": "Keep a slight bend; don't hyper-extend.",
        },
    ),
    # 4. Romanian Deadlift
    Exercise(
        name="Romanian Deadlift",
        slug="romanian_deadlift",
        category="lower",
        primary_muscles=["hamstrings", "glutes"],
        joints_to_track=["left_hip", "right_hip", "left_knee", "right_knee"],
        correct_angles={
            "left_hip": (90.0, 15.0),
            "right_hip": (90.0, 15.0),
            "left_knee": (160.0, 10.0),
            "right_knee": (160.0, 10.0),
        },
        rep_joint="left_hip",
        rep_angle_range=(80.0, 170.0),
        cues={
            "left_hip": "Hinge at the hips; push butt back.",
            "left_knee": "Keep knees almost straight with a soft bend.",
        },
    ),
    # 5. Bench Press
    Exercise(
        name="Bench Press",
        slug="bench_press",
        category="upper",
        primary_muscles=["pectorals", "anterior deltoid", "triceps"],
        joints_to_track=["left_elbow", "right_elbow", "left_shoulder", "right_shoulder"],
        correct_angles={
            "left_elbow": (90.0, 15.0),
            "right_elbow": (90.0, 15.0),
            "left_shoulder": (75.0, 15.0),
            "right_shoulder": (75.0, 15.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(80.0, 170.0),
        cues={
            "left_elbow": "Lower bar until elbows reach 90 degrees.",
            "right_elbow": "Lower bar until elbows reach 90 degrees.",
            "left_shoulder": "Tuck elbows ~75 degrees from torso; don't flare.",
            "right_shoulder": "Tuck elbows ~75 degrees from torso; don't flare.",
        },
    ),
    # 6. Overhead Press
    Exercise(
        name="Overhead Press",
        slug="overhead_press",
        category="upper",
        primary_muscles=["deltoids", "triceps", "upper chest"],
        joints_to_track=["left_elbow", "right_elbow", "left_shoulder", "right_shoulder"],
        correct_angles={
            "left_elbow": (170.0, 10.0),
            "right_elbow": (170.0, 10.0),
            "left_shoulder": (170.0, 15.0),
            "right_shoulder": (170.0, 15.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(85.0, 170.0),
        cues={
            "left_elbow": "Fully extend arms overhead at the top.",
            "left_shoulder": "Press straight up; don't lean back.",
        },
    ),
    # 7. Barbell Row
    Exercise(
        name="Barbell Row",
        slug="barbell_row",
        category="upper",
        primary_muscles=["latissimus dorsi", "rhomboids", "biceps"],
        joints_to_track=["left_elbow", "right_elbow", "left_hip", "right_hip"],
        correct_angles={
            "left_elbow": (90.0, 15.0),
            "right_elbow": (90.0, 15.0),
            "left_hip": (80.0, 15.0),
            "right_hip": (80.0, 15.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(80.0, 160.0),
        cues={
            "left_elbow": "Pull elbows back to 90 degrees; squeeze shoulder blades.",
            "left_hip": "Maintain a strong hip hinge; keep back flat.",
        },
    ),
    # 8. Push-up
    Exercise(
        name="Push-up",
        slug="pushup",
        category="upper",
        primary_muscles=["pectorals", "triceps", "anterior deltoid"],
        joints_to_track=["left_elbow", "right_elbow", "left_hip", "right_hip"],
        correct_angles={
            "left_elbow": (90.0, 15.0),
            "right_elbow": (90.0, 15.0),
            "left_hip": (180.0, 10.0),
            "right_hip": (180.0, 10.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(80.0, 170.0),
        cues={
            "left_elbow": "Lower until upper arms are parallel to the floor.",
            "left_hip": "Keep hips in line with shoulders and ankles; don't sag.",
        },
    ),
    # 9. Pull-up
    Exercise(
        name="Pull-up",
        slug="pullup",
        category="upper",
        primary_muscles=["latissimus dorsi", "biceps", "forearms"],
        joints_to_track=["left_elbow", "right_elbow", "left_shoulder", "right_shoulder"],
        correct_angles={
            "left_elbow": (45.0, 15.0),
            "right_elbow": (45.0, 15.0),
            "left_shoulder": (30.0, 15.0),
            "right_shoulder": (30.0, 15.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(40.0, 170.0),
        cues={
            "left_elbow": "Pull until chin clears the bar; elbows tight.",
            "left_shoulder": "Depress shoulders; don't shrug at the top.",
        },
    ),
    # 10. Dip
    Exercise(
        name="Dip",
        slug="dip",
        category="upper",
        primary_muscles=["triceps", "pectorals", "anterior deltoid"],
        joints_to_track=["left_elbow", "right_elbow", "left_shoulder", "right_shoulder"],
        correct_angles={
            "left_elbow": (90.0, 10.0),
            "right_elbow": (90.0, 10.0),
            "left_shoulder": (30.0, 15.0),
            "right_shoulder": (30.0, 15.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(80.0, 170.0),
        cues={
            "left_elbow": "Lower until elbows are at 90 degrees.",
            "left_shoulder": "Keep shoulders down and back; lean slightly forward.",
        },
    ),
    # 11. Plank
    Exercise(
        name="Plank",
        slug="plank",
        category="core",
        primary_muscles=["rectus abdominis", "transverse abdominis", "obliques"],
        joints_to_track=["left_hip", "right_hip", "left_shoulder", "right_shoulder"],
        correct_angles={
            "left_hip": (180.0, 10.0),
            "right_hip": (180.0, 10.0),
            "left_shoulder": (90.0, 10.0),
            "right_shoulder": (90.0, 10.0),
        },
        rep_joint="left_hip",
        rep_angle_range=(170.0, 180.0),
        cues={
            "left_hip": "Keep body in a straight line from head to heels.",
            "left_shoulder": "Stack shoulders directly over wrists.",
        },
    ),
    # 12. Side Plank
    Exercise(
        name="Side Plank",
        slug="side_plank",
        category="core",
        primary_muscles=["obliques", "gluteus medius"],
        joints_to_track=["left_hip", "right_hip"],
        correct_angles={
            "left_hip": (180.0, 10.0),
            "right_hip": (180.0, 10.0),
        },
        rep_joint="left_hip",
        rep_angle_range=(170.0, 180.0),
        cues={
            "left_hip": "Maintain a straight line; don't let hips drop.",
        },
    ),
    # 13. Lunge
    Exercise(
        name="Lunge",
        slug="lunge",
        category="lower",
        primary_muscles=["quadriceps", "glutes", "hamstrings"],
        joints_to_track=["left_knee", "right_knee", "left_hip", "right_hip"],
        correct_angles={
            "left_knee": (90.0, 15.0),
            "right_knee": (90.0, 15.0),
            "left_hip": (100.0, 15.0),
            "right_hip": (100.0, 15.0),
        },
        rep_joint="left_knee",
        rep_angle_range=(80.0, 170.0),
        cues={
            "left_knee": "Step far enough so front knee is at 90 degrees.",
            "left_hip": "Keep torso upright; don't lean forward.",
        },
    ),
    # 14. Bulgarian Split Squat
    Exercise(
        name="Bulgarian Split Squat",
        slug="bulgarian_split_squat",
        category="lower",
        primary_muscles=["quadriceps", "glutes"],
        joints_to_track=["left_knee", "right_knee", "left_hip", "right_hip"],
        correct_angles={
            "left_knee": (90.0, 15.0),
            "right_knee": (90.0, 20.0),
            "left_hip": (95.0, 15.0),
            "right_hip": (95.0, 15.0),
        },
        rep_joint="left_knee",
        rep_angle_range=(80.0, 165.0),
        cues={
            "left_knee": "Lower until front thigh is parallel to ground.",
            "left_hip": "Keep hips square; torso upright.",
        },
    ),
    # 15. Hip Thrust
    Exercise(
        name="Hip Thrust",
        slug="hip_thrust",
        category="lower",
        primary_muscles=["glutes", "hamstrings"],
        joints_to_track=["left_hip", "right_hip", "left_knee", "right_knee"],
        correct_angles={
            "left_hip": (180.0, 10.0),
            "right_hip": (180.0, 10.0),
            "left_knee": (90.0, 10.0),
            "right_knee": (90.0, 10.0),
        },
        rep_joint="left_hip",
        rep_angle_range=(90.0, 180.0),
        cues={
            "left_hip": "Thrust hips to full extension; squeeze glutes at the top.",
            "left_knee": "Keep shins vertical at the top of the movement.",
        },
    ),
    # 16. Bicep Curl
    Exercise(
        name="Bicep Curl",
        slug="bicep_curl",
        category="upper",
        primary_muscles=["biceps brachii", "brachialis"],
        joints_to_track=["left_elbow", "right_elbow", "left_shoulder", "right_shoulder"],
        correct_angles={
            "left_elbow": (40.0, 15.0),
            "right_elbow": (40.0, 15.0),
            "left_shoulder": (10.0, 10.0),
            "right_shoulder": (10.0, 10.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(35.0, 160.0),
        cues={
            "left_elbow": "Curl fully; squeeze at the top.",
            "left_shoulder": "Keep upper arms pinned to your sides; don't swing.",
        },
    ),
    # 17. Tricep Extension
    Exercise(
        name="Tricep Extension",
        slug="tricep_extension",
        category="upper",
        primary_muscles=["triceps"],
        joints_to_track=["left_elbow", "right_elbow"],
        correct_angles={
            "left_elbow": (170.0, 10.0),
            "right_elbow": (170.0, 10.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(70.0, 170.0),
        cues={
            "left_elbow": "Fully extend arms at the top; keep elbows tucked.",
        },
    ),
    # 18. Lateral Raise
    Exercise(
        name="Lateral Raise",
        slug="lateral_raise",
        category="upper",
        primary_muscles=["lateral deltoid"],
        joints_to_track=["left_shoulder", "right_shoulder", "left_elbow", "right_elbow"],
        correct_angles={
            "left_shoulder": (90.0, 15.0),
            "right_shoulder": (90.0, 15.0),
            "left_elbow": (160.0, 15.0),
            "right_elbow": (160.0, 15.0),
        },
        rep_joint="left_shoulder",
        rep_angle_range=(20.0, 90.0),
        cues={
            "left_shoulder": "Raise arms to shoulder height; no higher.",
            "left_elbow": "Keep a slight bend in the elbows throughout.",
        },
    ),
    # 19. Face Pull
    Exercise(
        name="Face Pull",
        slug="face_pull",
        category="upper",
        primary_muscles=["rear deltoid", "rhomboids", "external rotators"],
        joints_to_track=["left_elbow", "right_elbow", "left_shoulder", "right_shoulder"],
        correct_angles={
            "left_elbow": (90.0, 15.0),
            "right_elbow": (90.0, 15.0),
            "left_shoulder": (90.0, 15.0),
            "right_shoulder": (90.0, 15.0),
        },
        rep_joint="left_elbow",
        rep_angle_range=(80.0, 160.0),
        cues={
            "left_elbow": "Pull to face level; elbows high and wide.",
            "left_shoulder": "Externally rotate at the top; pinch shoulder blades.",
        },
    ),
    # 20. Calf Raise
    Exercise(
        name="Calf Raise",
        slug="calf_raise",
        category="lower",
        primary_muscles=["gastrocnemius", "soleus"],
        joints_to_track=["left_ankle", "right_ankle", "left_knee", "right_knee"],
        correct_angles={
            "left_ankle": (120.0, 15.0),
            "right_ankle": (120.0, 15.0),
            "left_knee": (175.0, 5.0),
            "right_knee": (175.0, 5.0),
        },
        rep_joint="left_ankle",
        rep_angle_range=(90.0, 130.0),
        cues={
            "left_ankle": "Rise fully onto toes; pause at the top.",
            "left_knee": "Keep legs straight; don't bend knees.",
        },
    ),
    # 21. Leg Press
    Exercise(
        name="Leg Press",
        slug="leg_press",
        category="lower",
        primary_muscles=["quadriceps", "glutes"],
        joints_to_track=["left_knee", "right_knee", "left_hip", "right_hip"],
        correct_angles={
            "left_knee": (90.0, 15.0),
            "right_knee": (90.0, 15.0),
            "left_hip": (90.0, 15.0),
            "right_hip": (90.0, 15.0),
        },
        rep_joint="left_knee",
        rep_angle_range=(80.0, 170.0),
        cues={
            "left_knee": "Lower sled until knees are at 90 degrees; don't lock out.",
            "left_hip": "Keep lower back flat against the pad.",
        },
    ),
    # 22. Leg Curl
    Exercise(
        name="Leg Curl",
        slug="leg_curl",
        category="lower",
        primary_muscles=["hamstrings"],
        joints_to_track=["left_knee", "right_knee"],
        correct_angles={
            "left_knee": (45.0, 15.0),
            "right_knee": (45.0, 15.0),
        },
        rep_joint="left_knee",
        rep_angle_range=(40.0, 170.0),
        cues={
            "left_knee": "Curl fully; control the eccentric.",
        },
    ),
]


class ExerciseDatabase:
    """In-memory catalogue of exercises with correct form angles."""

    def __init__(self) -> None:
        self._exercises: dict[str, Exercise] = {e.slug: e for e in _EXERCISES}

    @property
    def count(self) -> int:
        return len(self._exercises)

    def list_exercises(self) -> list[Exercise]:
        """Return all exercises sorted by name."""
        return sorted(self._exercises.values(), key=lambda e: e.name)

    def get(self, slug: str) -> Exercise | None:
        """Look up an exercise by slug."""
        return self._exercises.get(slug)

    def search(self, query: str) -> list[Exercise]:
        """Simple substring search across exercise names."""
        q = query.lower()
        return [e for e in self._exercises.values() if q in e.name.lower()]

    def categories(self) -> list[str]:
        """Return distinct categories."""
        return sorted({e.category for e in self._exercises.values()})

    def by_category(self, category: str) -> list[Exercise]:
        """Return exercises in a category."""
        return [e for e in self._exercises.values() if e.category == category]

    def add_exercise(self, exercise: Exercise) -> None:
        """Register a custom exercise."""
        self._exercises[exercise.slug] = exercise
