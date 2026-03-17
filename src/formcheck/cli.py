"""CLI entry-point for FormCheck."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from formcheck.exercises.database import ExerciseDatabase
from formcheck.exercises.workout import WorkoutTracker
from formcheck.pose.analyzer import FormAnalyzer
from formcheck.pose.corrector import FormCorrector
from formcheck.report import render_workout_report
from formcheck.simulator import PoseSimulator


console = Console()
db = ExerciseDatabase()


@click.group()
@click.version_option(package_name="formcheck")
def cli() -> None:
    """FormCheck - AI Personal Trainer with pose correction."""


@cli.command()
def exercises() -> None:
    """List all supported exercises."""
    table = Table(title=f"Supported Exercises ({db.count})", show_lines=True)
    table.add_column("#", style="dim", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Category")
    table.add_column("Muscles")
    table.add_column("Joints Tracked")

    for i, ex in enumerate(db.list_exercises(), 1):
        table.add_row(
            str(i),
            ex.name,
            ex.category,
            ", ".join(ex.primary_muscles),
            ", ".join(ex.joints_to_track),
        )
    console.print(table)


@cli.command()
@click.option(
    "--exercise",
    "-e",
    required=True,
    help="Exercise slug (e.g. squat, deadlift).",
)
@click.option("--reps", "-r", default=5, help="Number of reps per set.")
@click.option("--sets", "-s", default=3, help="Number of sets.")
@click.option(
    "--quality",
    "-q",
    default=0.85,
    help="Simulated form quality 0.0-1.0.",
)
@click.option("--seed", default=None, type=int, help="Random seed.")
def simulate(
    exercise: str,
    reps: int,
    sets: int,
    quality: float,
    seed: int | None,
) -> None:
    """Run a simulated workout and generate a report."""
    ex = db.get(exercise)
    if ex is None:
        console.print(f"[red]Unknown exercise: {exercise}[/red]")
        matches = db.search(exercise)
        if matches:
            console.print("Did you mean:")
            for m in matches:
                console.print(f"  - {m.slug}")
        raise SystemExit(1)

    console.print(f"Simulating {sets}x{reps} {ex.name} (quality={quality:.0%})...")

    sim = PoseSimulator(ex, form_quality=quality, seed=seed)
    analyzer = FormAnalyzer()
    corrector = FormCorrector(analyzer)
    tracker = WorkoutTracker(ex, analyzer, corrector)

    workout_data = sim.generate_workout(
        num_reps=reps,
        num_sets=sets,
        frames_per_rep=30,
    )

    for set_frames in workout_data:
        for rep_frames in set_frames:
            tracker.process_frames(rep_frames)
        tracker.end_set()

    result = tracker.finish_workout()
    render_workout_report(result, console)


@cli.command()
@click.option("--exercise", "-e", required=True, help="Exercise slug.")
@click.option("--video", "-v", required=True, help="Path to video file.")
def analyse(exercise: str, video: str) -> None:
    """Analyse form from a workout video (placeholder)."""
    ex = db.get(exercise)
    if ex is None:
        console.print(f"[red]Unknown exercise: {exercise}[/red]")
        raise SystemExit(1)
    console.print(
        f"[yellow]Video analysis for {ex.name} from {video} "
        f"is not yet implemented. Use 'simulate' for a demo.[/yellow]"
    )


if __name__ == "__main__":
    cli()
