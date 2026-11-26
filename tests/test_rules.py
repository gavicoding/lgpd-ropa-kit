from __future__ import annotations

import pytest

from conftest import ORG, base_op
from ropa_kit.loader import load_inventory
from ropa_kit.validate import ERROR, WARNING, dpia_reasons, has_errors, validate


def codes(folder, lang="pt"):
    return sorted((f.code, f.level) for f in validate(load_inventory(folder), lang))


def test_valid_operation_has_no_findings(make_inventory):
    assert codes(make_inventory(base_op())) == []


def test_sensitive_data_needs_art11_basis(make_inventory):
    folder = make_inventory(base_op(sensitive_data=["health"]))
    findings = validate(load_inventory(folder))
    r001 = [f for f in findings if f.code == "R001"]
    assert len(r001) == 1
    assert r001[0].level == ERROR
    assert r001[0].field == "sensitive_legal_basis"
    assert "health" in r001[0].message


def test_sensitive_data_with_art11_basis_passes(make_inventory):
    op = base_op(
        sensitive_data=["health"],
        sensitive_legal_basis="legal_obligation",
        dpia={"status": "done"},
    )
    assert codes(make_inventory(op)) == []


def test_art11_basis_without_sensitive_data_warns(make_inventory):
    assert codes(make_inventory(base_op(sensitive_legal_basis="consent"))) == [("R011", WARNING)]


@pytest.mark.parametrize("basis", ["contract", "legitimate_interest", "credit_protection"])
def test_bases_not_allowed_for_sensitive_data_are_rejected_by_schema(make_inventory, basis):
    op = base_op(sensitive_data=["biometric"], sensitive_legal_basis=basis)
    assert ("S001", ERROR) in codes(make_inventory(op))


def test_legitimate_interest_requires_lia(make_inventory):
    assert codes(make_inventory(base_op(legal_basis="legitimate_interest"))) == [("R002", ERROR)]


def test_lia_without_date_is_not_enough(make_inventory):
    op = base_op(legal_basis="legitimate_interest", lia={"reference": "LIA-1"})
    assert codes(make_inventory(op)) == [("R002", ERROR)]


def test_lia_with_date_passes(make_inventory):
    op = base_op(legal_basis="legitimate_interest", lia={"date": "2026-01-10", "outcome": "approved"})
    assert codes(make_inventory(op)) == []


def test_rejected_lia_is_an_error(make_inventory):
    op = base_op(legal_basis="legitimate_interest", lia={"date": "2026-01-10", "outcome": "rejected"})
    assert codes(make_inventory(op)) == [("R003", ERROR)]


@pytest.mark.parametrize("retention", [None, {}, {"period": "  "}, {"justification": "lei"}])
def test_retention_is_required(make_inventory, retention):
    op = base_op(retention=retention)
    if retention is None:
        op.pop("retention", None)
    assert codes(make_inventory(op)) == [("R004", ERROR)]


def test_international_transfer_needs_mechanism(make_inventory):
    op = base_op(international_transfers=[{"country": "US"}, {"country": "DE", "mechanism": "adequacy"}])
    findings = validate(load_inventory(make_inventory(op)))
    assert [(f.code, f.field) for f in findings] == [("R005", "international_transfers[0].mechanism")]
    assert "US" in findings[0].message


@pytest.mark.parametrize(
    ("proc", "expected"),
    [
        ({"name": "Op A", "contract": True, "dpa": True}, []),
        ({"name": "Op A", "contract": True}, [("R006", WARNING)]),
        ({"name": "Op A"}, [("R006", WARNING)]),
    ],
)
def test_processor_without_contract_or_dpa_warns(make_inventory, proc, expected):
    assert codes(make_inventory(base_op(processors=[proc]))) == expected


def test_processor_message_lists_what_is_missing(make_inventory):
    findings = validate(load_inventory(make_inventory(base_op(processors=[{"name": "Op A"}]))))
    assert "contrato e cláusulas" in findings[0].message
    findings = validate(load_inventory(make_inventory(base_op(processors=[{"name": "Op A"}]))), "en")
    assert "a contract and data processing clauses" in findings[0].message


def test_high_risk_without_completed_dpia_warns(make_inventory):
    op = base_op(risk={"likelihood": 4, "impact": 3})
    assert codes(make_inventory(op)) == [("R007", WARNING)]
    op["dpia"] = {"status": "in_progress"}
    assert codes(make_inventory(op)) == [("R007", WARNING)]
    op["dpia"] = {"status": "done"}
    assert codes(make_inventory(op)) == []


def test_dpia_reasons():
    assert dpia_reasons(base_op()) == []
    assert dpia_reasons(base_op(risk={"likelihood": 3, "impact": 4})) == ["pontuação 12"]
    assert dpia_reasons(base_op(children_data=True), "en") == ["children's data"]
    forced = base_op(risk={"likelihood": 1, "impact": 1, "requires_dpia": True})
    assert dpia_reasons(forced) == ["marcada manualmente"]
    opted_out = base_op(
        sensitive_data=["health"], risk={"likelihood": 5, "impact": 5, "requires_dpia": False}
    )
    assert dpia_reasons(opted_out) == []


def test_missing_security_measures_warns(make_inventory):
    assert codes(make_inventory(base_op(security_measures=[]))) == [("R008", WARNING)]


def test_duplicate_ids_are_errors(make_inventory):
    findings = validate(load_inventory(make_inventory(base_op(), base_op())))
    dup = [f for f in findings if f.code == "R009"]
    assert len(dup) == 1
    assert "00-op-teste.yaml" in dup[0].message


def test_dpo_contact_is_expected(make_inventory):
    org = {"controller": ORG["controller"], "dpo": {"name": "Alguém"}}
    assert codes(make_inventory(base_op(), org=org)) == [("R010", WARNING)]


def test_empty_inventory_warns(make_inventory):
    assert codes(make_inventory()) == [("R012", WARNING)]


def test_has_errors():
    assert not has_errors([])
