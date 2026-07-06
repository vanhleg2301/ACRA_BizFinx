"""Console + markdown validation report."""
from pathlib import Path

from rich.console import Console
from rich.table import Table

_console = Console()


def print_validation_report(
    mismatches: list[dict], unmapped: list[str], sign_warnings: list[dict] | None = None,
) -> None:
    if mismatches:
        _console.print("\n[bold red]CALC MISMATCHES[/bold red]")
        t = Table("Rule", "Context", "Computed", "Reported", "Diff")
        for m in mismatches:
            t.add_row(
                m["rule"], m["context"],
                f"{m['computed']:.2f}", f"{m['reported']:.2f}", f"{m['diff']:.2f}",
            )
        _console.print(t)
    else:
        _console.print("\n[bold green]PASS: All calc rules pass[/bold green]")

    if unmapped:
        _console.print(f"\n[yellow]Unmapped labels ({len(unmapped)}):[/yellow]")
        for label in unmapped:
            _console.print(f"  - {label}")
    else:
        _console.print("[green]PASS: All labels mapped[/green]")

    if sign_warnings:
        _console.print(
            f"\n[yellow]Sign warnings ({len(sign_warnings)}) — BizFinX will likely flag "
            "these, fix the source Excel and re-run:[/yellow]"
        )
        for w in sign_warnings:
            _console.print(f"  - {w['element']} [{w['context']}] = {w['value']:.2f}")
    else:
        _console.print("[green]PASS: No negative-sign warnings[/green]")


def write_unmapped_report(unmapped: list[str], output_dir: Path, uen: str) -> Path | None:
    if not unmapped:
        return None
    path = output_dir / f"{uen}_unmapped_report.md"
    lines = [
        f"# Unmapped Labels — {uen}\n",
        "These labels were found in the Excel input but have no entry in `mapping.yaml`.\n",
        "Add a mapping entry for each and re-run.\n\n",
    ]
    for label in unmapped:
        lines.append(f"- `{label}`\n")
    path.write_text("".join(lines), encoding="utf-8")
    return path


def write_validation_md(
    mismatches: list[dict], output_dir: Path, uen: str, sign_warnings: list[dict] | None = None,
) -> Path:
    path = output_dir / f"{uen}_validation.md"
    lines = [f"# Validation — {uen}\n\n## Calc Mismatches\n\n"]
    if not mismatches:
        lines.append("✓ All calc rules pass.\n\n")
    else:
        lines += ["| Rule | Context | Computed | Reported | Diff |\n",
                  "|------|---------|----------|----------|------|\n"]
        for m in mismatches:
            lines.append(
                f"| {m['rule']} | {m['context']} | {m['computed']:.2f} "
                f"| {m['reported']:.2f} | {m['diff']:.2f} |\n"
            )
        lines.append("\n")

    lines.append("## Sign Warnings\n\n")
    if not sign_warnings:
        lines.append("✓ No negative-sign warnings.\n")
    else:
        lines.append(
            "These elements are expected to be entered as positive magnitudes "
            "(BizFinX's own validator will likely flag them as \"Possible Error\" "
            "otherwise). Fix the source Excel value and re-run.\n\n"
        )
        lines += ["| Element | Context | Value |\n", "|---------|---------|-------|\n"]
        for w in sign_warnings:
            lines.append(f"| {w['element']} | {w['context']} | {w['value']:.2f} |\n")

    path.write_text("".join(lines), encoding="utf-8")
    return path
