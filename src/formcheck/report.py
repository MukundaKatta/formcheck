"""Report - rich console reports summarising workout quality."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from formcheck.models import SetResult, Severity, WorkoutResult


def _score_colour(score: float) -> str:
    if score >= 85:
        return "green"
    if score >= 65:
        return "yellow"
    return "red"


def render_set_table(set_result: SetResult, console: Console | None = None) -> None:
    """Print a rich table for a single set."""
    console = console or Console()
    table = Table(
        title=f"{set_result.exercise_name} - Set {set_result.set_number}",
        show_lines=True,
    )
    table.add_column("Rep", style="bold", justify="center")
    table.add_column("Score", justify="center")
    table.add_column("Duration (s)", justify="center")
    table.add_column("Corrections", style="dim")

    for rep in set_result.reps:
        colour = _score_colour(rep.form_score.overall)
        score_text = Text(f"{rep.form_score.overall:.1f}", style=colour)
        corrections = "; ".join(c.message for c in rep.form_score.corrections) or "-"
        table.add_row(
            str(rep.rep_number),
            score_text,
            f"{rep.duration_seconds:.2f}",
            corrections,
        )

    avg_colour = _score_colour(set_result.average_score)
    table.add_row(
        "AVG",
        Text(f"{set_result.average_score:.1f}", style=f"bold {avg_colour}"),
        "-",
        "",
    )
    console.print(table)


def render_workout_report(
    result: WorkoutResult,
    console: Console | None = None,
) -> None:
    """Print a full workout summary report."""
    console = console or Console()
    console.print()
    console.print(
        Panel(
            f"[bold]{result.exercise_name}[/bold]  |  "
            f"Sets: {len(result.sets)}  |  "
            f"Total reps: {result.total_reps}  |  "
            f"Average form: {result.average_form_score:.1f}/100",
            title="Workout Summary",
            border_style="blue",
        )
    )

    for set_result in result.sets:
        render_set_table(set_result, console)

    if result.corrections_summary:
        console.print()
        corr_table = Table(title="Correction Frequency", show_lines=True)
        corr_table.add_column("Joint", style="bold")
        corr_table.add_column("Times Flagged", justify="center")

        for joint, count in sorted(
            result.corrections_summary.items(), key=lambda x: -x[1]
        ):
            severity_style = "red" if count > 3 else "yellow"
            corr_table.add_row(
                joint.replace("_", " ").title(),
                Text(str(count), style=severity_style),
            )
        console.print(corr_table)

    overall_colour = _score_colour(result.average_form_score)
    console.print()
    if result.average_form_score >= 85:
        console.print(
            f"[bold {overall_colour}]Excellent form! Keep it up.[/bold {overall_colour}]"
        )
    elif result.average_form_score >= 65:
        console.print(
            f"[bold {overall_colour}]Decent form. Review the corrections above.[/bold {overall_colour}]"
        )
    else:
        console.print(
            f"[bold {overall_colour}]Form needs work. Consider reducing weight and focusing on technique.[/bold {overall_colour}]"
        )
    console.print()
