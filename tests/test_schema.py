from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import base_op
from ropa_kit.legal import ART7, ART11, ART33, SENSITIVE
from ropa_kit.loader import InventoryError, load_inventory, load_schema
from ropa_kit.validate import validate

ROOT = Path(__file__).resolve().parents[1]


def schema_errors(folder, lang="pt"):
    return [(f.field, f.message) for f in validate(load_inventory(folder), lang) if f.code == "S001"]


def test_published_schema_matches_the_packaged_one():
    published = json.loads((ROOT / "schema" / "ropa.schema.json").read_text(encoding="utf-8"))
    assert published == load_schema()


@pytest.mark.parametrize(
    ("definition", "catalog"),
    [("art7", ART7), ("art11", ART11), ("art33", ART33), ("sensitiveCategory", SENSITIVE)],
)
def test_schema_enums_match_the_legal_catalog(definition, catalog):
    assert load_schema()["$defs"][definition]["enum"] == list(catalog)


def test_missing_required_field(make_inventory):
    op = base_op()
    del op["purpose"]
    assert schema_errors(make_inventory(op)) == [("purpose", "campo obrigatório ausente: purpose")]


def test_unknown_field_is_reported(make_inventory):
    errors = schema_errors(make_inventory(base_op(legal_bassis="consent")))
    assert errors == [("legal_bassis", "campo desconhecido: legal_bassis")]


def test_invalid_enum_lists_the_options(make_inventory):
    errors = schema_errors(make_inventory(base_op(legal_basis="vontade")), "en")
    assert errors[0][0] == "legal_basis"
    assert "'vontade' is not allowed" in errors[0][1]
    assert "legitimate_interest" in errors[0][1]


def test_wrong_type_and_range(make_inventory):
    errors = schema_errors(make_inventory(base_op(children_data="sim", risk={"likelihood": 9, "impact": 1})))
    fields = dict(errors)
    assert fields["children_data"].startswith("tipo errado")
    assert fields["risk.likelihood"] == "valor fora do intervalo de 1 a 5"


def test_bad_id_and_date_format(make_inventory):
    op = base_op(id="Op Teste", dpia={"status": "done", "date": "10/05/2026"})
    fields = dict(schema_errors(make_inventory(op)))
    assert fields["id"] == "formato inválido: 'Op Teste'"
    assert fields["dpia.date"] == "formato inválido: '10/05/2026'"


def test_empty_list_and_duplicates(make_inventory):
    op = base_op(personal_data=[], sensitive_data=["health", "health"], sensitive_legal_basis="consent")
    fields = dict(schema_errors(make_inventory(op)))
    assert fields["personal_data"] == "não pode ficar vazio"
    assert fields["sensitive_data"] == "itens repetidos na lista"


def test_nested_list_path(make_inventory):
    op = base_op(processors=[{"name": "ok", "contract": True, "dpa": True}, {"service": "sem nome"}])
    assert schema_errors(make_inventory(op))[0][0] == "processors[1].name"


def test_dates_stay_strings(make_inventory):
    folder = make_inventory(base_op())
    (folder / "organization.yaml").write_text(
        "controller: {name: Empresa Exemplo Ltda}\nreviewed_at: 2026-11-01\n", encoding="utf-8"
    )
    inventory = load_inventory(folder)
    assert inventory.org["reviewed_at"] == "2026-11-01"
    assert schema_errors(folder) == []


def test_yaml_syntax_error(make_inventory):
    folder = make_inventory(raw={"operations/quebrado.yaml": "id: [aberto\nname: x\n"})
    findings = validate(load_inventory(folder))
    assert [(f.code, f.file) for f in findings] == [("Y001", "operations/quebrado.yaml")]
    assert "line" in findings[0].message


def test_unreadable_file_is_a_finding_not_a_crash(make_inventory):
    folder = make_inventory(base_op())
    (folder / "operations" / "pasta.yaml").mkdir()
    findings = validate(load_inventory(folder))
    assert [(f.code, f.file) for f in findings] == [("Y001", "operations/pasta.yaml")]
    assert "cannot read file" in findings[0].message


def test_file_that_is_not_a_mapping(make_inventory):
    folder = make_inventory(raw={"operations/lista.yml": "- a\n- b\n"})
    assert [f.code for f in validate(load_inventory(folder))] == ["Y002"]


def test_missing_folder_and_organization(tmp_path):
    with pytest.raises(InventoryError, match="folder not found"):
        load_inventory(tmp_path / "nada")
    with pytest.raises(InventoryError, match=r"organization\.yaml"):
        load_inventory(tmp_path)
