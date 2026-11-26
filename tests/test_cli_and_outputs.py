from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from conftest import base_op
from ropa_kit.cli import main
from ropa_kit.loader import load_inventory
from ropa_kit.report import render_report
from ropa_kit.ripd import render_ripd
from ropa_kit.validate import validate

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "empresa-exemplo"


def tree(folder: Path) -> dict[str, bytes]:
    return {
        p.relative_to(folder).as_posix(): p.read_bytes().replace(b"\r\n", b"\n")
        for p in sorted(folder.rglob("*.yaml"))
    }


def test_init_creates_the_example_and_matches_the_repository_copy(tmp_path, capsys):
    target = tmp_path / "novo"
    assert main(["init", str(target)]) == 0
    assert "12" in capsys.readouterr().out
    assert tree(target) == tree(EXAMPLE)


def test_init_refuses_non_empty_folder(tmp_path, capsys):
    (tmp_path / "algo.txt").write_text("x", encoding="utf-8")
    assert main(["init", str(tmp_path)]) == 2
    assert "não está vazia" in capsys.readouterr().err


def test_validate_example_reports_the_planted_issues(capsys):
    assert main(["validate", str(EXAMPLE)]) == 1
    out = capsys.readouterr().out
    for code in ("R002", "R004", "R005", "R006", "R007", "R008"):
        assert code in out
    assert "12 operações · 3 erro(s) · 4 aviso(s)" in out


def test_validate_json_output(capsys):
    assert main(["validate", str(EXAMPLE), "--format", "json", "--lang", "en"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["operations"] == 12
    assert payload["errors"] == 3
    assert {f["operation"] for f in payload["findings"]} >= {"ti-cftv", "mkt-perfil-de-consumo"}


def test_validate_clean_and_strict(make_inventory, capsys):
    clean = make_inventory(base_op())
    assert main(["validate", str(clean)]) == 0
    assert "Nenhum problema" in capsys.readouterr().out
    warn_only = make_inventory(base_op(security_measures=[]))
    assert main(["validate", str(warn_only)]) == 0
    assert main(["validate", str(warn_only), "--strict"]) == 1


def test_lang_before_or_after_subcommand(make_inventory, capsys):
    folder = make_inventory(base_op())
    main(["--lang", "en", "validate", str(folder)])
    main(["validate", str(folder), "--lang", "en"])
    out = capsys.readouterr().out
    assert out.count("No issues found.") == 2


def test_missing_folder_exit_code(tmp_path, capsys):
    assert main(["validate", str(tmp_path / "nada")]) == 2
    assert "folder not found" in capsys.readouterr().err


def test_report_command(tmp_path, capsys):
    out = tmp_path / "sub" / "r.html"
    assert main(["report", str(EXAMPLE), "-o", str(out), "--date", "2026-11-26"]) == 1
    html = out.read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>")
    assert "Relatório gerado em 2026-11-26" in html


def test_report_contents():
    inventory = load_inventory(EXAMPLE)
    html = render_report(inventory, validate(inventory), "pt", date(2026, 11, 26))
    # index by area and every operation
    for area in ("Atendimento", "Financeiro", "Marketing", "RH", "TI"):
        assert f"href='#area-{area}'" in html
    for op in inventory.valid_operations:
        assert f"id='op-{op['id']}'" in html
    assert "<span class='tag sens' title='sensível'>Dado biométrico</span>" in html
    assert "art. 11, II, g" in html  # sensitive legal basis
    assert "GDPR art. 6(1)(f)" in html
    assert "Cláusulas-padrão contratuais" in html  # art. 33 mechanism
    assert "class='matrix'" in html
    assert html.count("class='lvl-error'") == 3
    assert "<script" not in html  # self-contained, no scripts


def test_report_escapes_html(make_inventory):
    folder = make_inventory(base_op(name="<script>alert(1)</script>"))
    inventory = load_inventory(folder)
    html = render_report(inventory, validate(inventory), "en", date(2026, 1, 1))
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_report_skips_broken_operations(make_inventory):
    folder = make_inventory(base_op(id="boa"), base_op(id="ruim", legal_basis="x"))
    inventory = load_inventory(folder)
    html = render_report(inventory, validate(inventory), "pt", date(2026, 1, 1))
    assert "id='op-boa'" in html
    assert "id='op-ruim'" not in html
    assert "ficam fora das tabelas" in html


def test_sample_report_in_docs_is_up_to_date():
    inventory = load_inventory(EXAMPLE)
    expected = render_report(inventory, validate(inventory), "pt", date(2026, 11, 26))
    current = (ROOT / "docs" / "sample-report.html").read_text(encoding="utf-8")
    assert current.replace("\r\n", "\n") == expected, "run: ropa-kit report examples/empresa-exemplo ..."


def test_ripd_command(tmp_path, capsys):
    out = tmp_path / "ripd.md"
    assert main(["ripd", str(EXAMPLE), "rh-ponto-biometrico", "-o", str(out), "--date", "2026-11-26"]) == 0
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Relatório de Impacto")
    assert "pontuação 12" in text
    assert "Dado biométrico" in text
    assert "art. 11, II, g" in text
    assert "probabilidade 3, impacto 4, pontuação 12" in text


def test_ripd_unknown_operation(capsys):
    assert main(["ripd", str(EXAMPLE), "nao-existe"]) == 2
    assert "rh-folha-pagamento" in capsys.readouterr().err


@pytest.mark.parametrize("lang", ["pt", "en"])
def test_ripd_all_sections(lang):
    op = base_op(
        legal_basis="legitimate_interest",
        lia={"date": "2026-01-10", "reference": "LIA-1"},
        international_transfers=[{"country": "US", "mechanism": "standard_clauses"}],
        children_data=True,
    )
    text = render_ripd(op, {"controller": {"name": "Empresa Exemplo Ltda"}}, lang, date(2026, 1, 1))
    assert text.count("\n## ") == 8
    assert "LIA-1" in text
    assert "US (art. 33, II, b)" in text


def test_schema_command(capsys):
    assert main(["schema"]) == 0
    assert json.loads(capsys.readouterr().out)["title"] == "lgpd-ropa-kit inventory"


def test_module_entry_point():
    import runpy

    with pytest.raises(SystemExit) as exc:
        import sys

        sys.argv = ["ropa-kit", "--version"]
        runpy.run_module("ropa_kit", run_name="__main__")
    assert exc.value.code == 0
