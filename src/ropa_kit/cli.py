"""Command line interface: ``ropa-kit init | validate | report | ripd | schema``."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from importlib import resources
from pathlib import Path
from typing import Any

from . import __version__
from .loader import InventoryError, load_inventory, load_schema
from .messages import LANGS
from .report import render_report
from .ripd import render_ripd
from .validate import ERROR, has_errors, validate

EXIT_OK, EXIT_INVALID, EXIT_USAGE = 0, 1, 2

TEXT = {
    "pt": {
        "init_done": "Exemplo criado em {path} ({count} operações fictícias).",
        "init_exists": "{path} já existe e não está vazia; escolha outra pasta.",
        "summary": "{ops} operações · {errors} erro(s) · {warnings} aviso(s)",
        "ok": "Nenhum problema encontrado.",
        "report_done": "Relatório salvo em {path}",
        "ripd_done": "RIPD salvo em {path}",
        "no_op": "operação '{id}' não encontrada; ids disponíveis: {ids}",
        "error": "erro",
        "warning": "aviso",
    },
    "en": {
        "init_done": "Example created in {path} ({count} fictional operations).",
        "init_exists": "{path} already exists and is not empty; pick another folder.",
        "summary": "{ops} operations · {errors} error(s) · {warnings} warning(s)",
        "ok": "No issues found.",
        "report_done": "Report saved to {path}",
        "ripd_done": "DPIA saved to {path}",
        "no_op": "operation '{id}' not found; available ids: {ids}",
        "error": "error",
        "warning": "warning",
    },
}


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}") from exc


def _copy_tree(src: Any, dst: Path) -> int:
    """Copy the packaged sample (an importlib.resources Traversable) to ``dst``."""
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in sorted(src.iterdir(), key=lambda i: i.name):
        if item.is_dir():
            count += _copy_tree(item, dst / item.name)
        elif item.name.endswith((".yaml", ".yml")):
            (dst / item.name).write_bytes(item.read_bytes())
            count += 1
    return count


def cmd_init(args: argparse.Namespace, t: dict) -> int:
    target = Path(args.folder)
    if target.exists() and any(target.iterdir()):
        print(t["init_exists"].format(path=target), file=sys.stderr)
        return EXIT_USAGE
    _copy_tree(resources.files("ropa_kit").joinpath("sample"), target)
    count = len(list((target / "operations").glob("*.yaml")))
    print(t["init_done"].format(path=target, count=count))
    return EXIT_OK


def cmd_validate(args: argparse.Namespace, t: dict) -> int:
    inventory = load_inventory(args.folder)
    findings = validate(inventory, args.lang)
    errors = sum(1 for f in findings if f.level == ERROR)
    if args.format == "json":
        payload = {
            "operations": len(inventory.operations),
            "errors": errors,
            "warnings": len(findings) - errors,
            "findings": [f.to_dict() for f in findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for f in sorted(findings, key=lambda f: (f.file, f.level != ERROR, f.code)):
            where = f"{f.file}: {f.field}" if f.field else f.file
            print(f"{where}: {t[f.level]} {f.code}: {f.message}")
        if findings:
            print()
        print(
            t["summary"].format(ops=len(inventory.operations), errors=errors, warnings=len(findings) - errors)
        )
        if not findings:
            print(t["ok"])
    failed = has_errors(findings) or (args.strict and bool(findings))
    return EXIT_INVALID if failed else EXIT_OK


def cmd_report(args: argparse.Namespace, t: dict) -> int:
    inventory = load_inventory(args.folder)
    findings = validate(inventory, args.lang)
    html = render_report(inventory, findings, args.lang, args.date)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    print(t["report_done"].format(path=out))
    return EXIT_INVALID if has_errors(findings) else EXIT_OK


def cmd_ripd(args: argparse.Namespace, t: dict) -> int:
    inventory = load_inventory(args.folder)
    ops = {op.get("id"): op for op in inventory.valid_operations}
    op = ops.get(args.operation)
    if op is None or not op.get("name"):
        ids = ", ".join(sorted(str(i) for i in ops if i)) or "-"
        print(t["no_op"].format(id=args.operation, ids=ids), file=sys.stderr)
        return EXIT_USAGE
    text = render_ripd(op, inventory.org, args.lang, args.date)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(t["ripd_done"].format(path=out))
    return EXIT_OK


def cmd_schema(_args: argparse.Namespace, _t: dict) -> int:
    print(json.dumps(load_schema(), ensure_ascii=False, indent=2))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    # --lang works before or after the subcommand. The subcommand copy uses SUPPRESS so it does
    # not overwrite a value given before the subcommand with its own default.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lang", choices=LANGS, default=argparse.SUPPRESS, help="pt (default) or en")

    parser = argparse.ArgumentParser(
        prog="ropa-kit",
        description="LGPD Record of Processing Activities as versioned YAML.",
    )
    parser.add_argument("--lang", choices=LANGS, default="pt", help="pt (default) or en")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", parents=[common], help="create an example inventory with fictional data")
    p.add_argument("folder", nargs="?", default="ropa-exemplo")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("validate", parents=[common], help="check schema and LGPD rules")
    p.add_argument("folder")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.add_argument("--strict", action="store_true", help="warnings also fail (exit 1)")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("report", parents=[common], help="write the self-contained HTML report")
    p.add_argument("folder")
    p.add_argument("-o", "--output", default="relatorio.html")
    p.add_argument("--date", type=_parse_date, help="date printed on the report (YYYY-MM-DD)")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("ripd", parents=[common], help="write a DPIA (RIPD) skeleton in Markdown")
    p.add_argument("folder")
    p.add_argument("operation", help="operation id")
    p.add_argument("-o", "--output", default="ripd.md")
    p.add_argument("--date", type=_parse_date, help="date printed on the draft (YYYY-MM-DD)")
    p.set_defaults(func=cmd_ripd)

    p = sub.add_parser("schema", parents=[common], help="print the JSON schema")
    p.set_defaults(func=cmd_schema)
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    args = build_parser().parse_args(argv)
    t = TEXT[args.lang]
    try:
        return args.func(args, t)
    except InventoryError as exc:
        print(f"ropa-kit: {exc}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
