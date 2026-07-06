"""
acra-helper CLI

Usage:
    acra-helper run --company <UEN> [--skip-validation]
    acra-helper run --company 201631437H
"""
import argparse
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent.parent  # repo root


def _find_input(inputs_dir: Path, uen: str, suffixes: list[str]) -> Path | None:
    for suffix in suffixes:
        for path in inputs_dir.glob(f"{uen}*{suffix}"):
            return path
    return None


def run_company(uen: str, skip_validation: bool = False, generate_xbrl: bool = False) -> int:
    from rich.console import Console
    import yaml

    from acra_helper.taxonomy import load_calc_rules, load_contexts_seed
    from acra_helper.taxonomy.contexts import build_contexts
    from acra_helper.validate.calc_validator import build_numeric_fact_index, validate, check_signs
    from acra_helper.mapping.engine import load_mapping, apply_mapping
    from acra_helper.generate.prefill_writer import write_prefill
    from acra_helper.generate.report import (
        print_validation_report, write_unmapped_report, write_validation_md,
    )

    console = Console()
    company_dir = BASE / "companies" / uen
    inputs_dir = BASE / "inputs"
    output_dir = BASE / "output"

    if not company_dir.exists():
        console.print(f"[red]Company directory not found: {company_dir}[/red]")
        return 1

    profile_path = company_dir / "profile.yaml"
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))

    from datetime import date
    fye_str = profile["fye"]  # "2025-12-31"
    fye = date.fromisoformat(fye_str)
    contexts = build_contexts(fye)

    # ── 1. Parse Excel (optional) ────────────────────────────────────────────
    mapped_facts: list[dict] = []
    unmapped: list[str] = []

    xlsx_path = _find_input(inputs_dir, uen, [".xlsx", ".xls"])
    if xlsx_path:
        from acra_helper.parser.excel_parser import parse_excel
        from acra_helper.mapping.engine import load_mapping, apply_mapping

        console.print(f"Parsing Excel: {xlsx_path.name}")
        parsed = parse_excel(xlsx_path)
        mappings = load_mapping(company_dir / "mapping.yaml")
        mapped_facts, unmapped = apply_mapping(parsed, mappings)
        console.print(f"  Mapped: {len(mapped_facts)} facts, Unmapped: {len(unmapped)} labels")
    else:
        console.print("[yellow]No Excel input found — skipping parse step[/yellow]")

    # ── 2. Parse Word (optional) ─────────────────────────────────────────────
    rtf_text = ""
    docx_path = _find_input(inputs_dir, uen, [".docx", ".doc"])
    if docx_path:
        from acra_helper.parser.word_parser import parse_word
        from acra_helper.mapping.rtf_builder import build_rtf

        console.print(f"Parsing Word: {docx_path.name}")
        parsed_word = parse_word(docx_path)
        rtf_text = build_rtf(parsed_word["full_text"])
        mapped_facts.append({
            "element": "sg-as:DisclosureOfCompleteSetOfFinancialStatementsTextBlock",
            "context": f"fromto_{fye.year-1+1:04d}0101_{fye.strftime('%Y%m%d')}",
            "value": rtf_text,
        })
    else:
        console.print("[yellow]No Word input found — skipping FS text block[/yellow]")

    # ── 3. Validate ──────────────────────────────────────────────────────────
    mismatches: list[dict] = []
    sign_warnings: list[dict] = []
    if not skip_validation and mapped_facts:
        calc_rules = load_calc_rules()
        index = build_numeric_fact_index(mapped_facts)
        mismatches = validate(index, calc_rules)
        sign_warnings = check_signs(mapped_facts, calc_rules)

    print_validation_report(mismatches, unmapped, sign_warnings)

    # ── 4. Write unmapped report ─────────────────────────────────────────────
    if unmapped:
        report_path = write_unmapped_report(unmapped, output_dir, uen)
        console.print(f"Unmapped report: {report_path}")

    write_validation_md(mismatches, output_dir, uen, sign_warnings)

    # ── 5. Write pre-fill ────────────────────────────────────────────────────
    if mapped_facts:
        if generate_xbrl:
            from acra_helper.generate.xbrl_writer import write_xbrl_package
            pkg_dir = write_xbrl_package(
                facts=mapped_facts,
                contexts=contexts,
                output_dir=output_dir,
                uen=uen,
                name=profile["name"],
                fye=fye,
                currency=profile.get("currency", "SGD"),
                address=profile.get("address", ""),
            )
            console.print(f"\n[bold green]XBRL package written:[/bold green] {pkg_dir}")
            for f in sorted(pkg_dir.iterdir()):
                console.print(f"  {f.name}")
        else:
            xlsx_out, json_out = write_prefill(mapped_facts, contexts, output_dir, uen)
            console.print(f"\nPre-fill written:")
            console.print(f"  {xlsx_out}")
            console.print(f"  {json_out}")
    else:
        console.print("[yellow]No facts to write — provide Excel/Word input files[/yellow]")

    return 1 if mismatches else 0


def demo() -> int:
    """Generate an XBRL package from seed data (no Excel/Word needed)."""
    from rich.console import Console
    from datetime import date
    import json

    from acra_helper.taxonomy import load_fact_map_seed, load_contexts_seed
    from acra_helper.taxonomy.contexts import build_contexts
    from acra_helper.validate.calc_validator import build_numeric_fact_index, validate, check_signs
    from acra_helper.taxonomy import load_calc_rules
    from acra_helper.generate.xbrl_writer import write_xbrl_package
    from acra_helper.generate.report import print_validation_report

    console = Console()
    console.print("[bold cyan]Demo mode — using EVX Ventures seed data[/bold cyan]\n")

    seed = load_fact_map_seed()
    facts = seed["facts"]
    fye = date(2025, 12, 31)
    contexts = build_contexts(fye)

    # validate first
    calc_rules = load_calc_rules()
    index = build_numeric_fact_index(facts)
    mismatches = validate(index, calc_rules)
    sign_warnings = check_signs(facts, calc_rules)
    print_validation_report(mismatches, [], sign_warnings)

    if mismatches:
        console.print("[red]Seed data has calc mismatches — aborting[/red]")
        return 1

    output_dir = BASE / "output"
    pkg_dir = write_xbrl_package(
        facts=facts,
        contexts=contexts,
        output_dir=output_dir,
        uen="201631437H",
        name="EVX VENTURES PTE. LTD.",
        fye=fye,
        currency="SGD",
        address="19, Changi South Street 1, Singapore 486779",
    )
    console.print(f"\n[bold green]Package written: {pkg_dir}[/bold green]")
    for f in sorted(pkg_dir.iterdir()):
        size = f.stat().st_size
        console.print(f"  {f.name:<45} {size:>8,} bytes")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="acra-helper")
    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run", help="Process a company filing")
    run_cmd.add_argument("--company", required=True, help="Company UEN")
    run_cmd.add_argument("--skip-validation", action="store_true")
    run_cmd.add_argument("--xbrl", action="store_true",
                         help="Generate full XBRL package (8 files) instead of pre-fill only")

    sub.add_parser("demo", help="Generate XBRL from built-in EVX seed data (no input files needed)")

    args = parser.parse_args()

    if args.command == "run":
        sys.exit(run_company(args.company, skip_validation=args.skip_validation,
                             generate_xbrl=args.xbrl))
    elif args.command == "demo":
        sys.exit(demo())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
