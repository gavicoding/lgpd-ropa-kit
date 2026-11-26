"""Schema validation plus the business rules of the LGPD."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .loader import Inventory, load_schema
from .messages import msg, word

ERROR = "error"
WARNING = "warning"

# A DPIA (RIPD) is expected when likelihood x impact reaches this score.
HIGH_RISK_SCORE = 12


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    file: str
    field: str
    message: str
    operation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def risk_score(op: dict) -> int | None:
    risk = op.get("risk")
    if not isinstance(risk, dict):
        return None
    likelihood, impact = risk.get("likelihood"), risk.get("impact")
    if isinstance(likelihood, int) and isinstance(impact, int):
        return likelihood * impact
    return None


def dpia_reasons(op: dict, lang: str = "pt") -> list[str]:
    """Why the operation needs a DPIA (RIPD). Empty list means it does not."""
    risk = op.get("risk") if isinstance(op.get("risk"), dict) else {}
    forced = risk.get("requires_dpia")
    if forced is False:
        return []
    reasons = []
    if forced is True:
        reasons.append(word("forced", lang))
    score = risk_score(op)
    if score is not None and score >= HIGH_RISK_SCORE:
        reasons.append(word("score", lang, score=score))
    if op.get("sensitive_data"):
        reasons.append(word("sensitive", lang))
    if op.get("children_data"):
        reasons.append(word("children", lang))
    return reasons


def _path(error: ValidationError) -> str:
    parts = []
    for part in error.absolute_path:
        if isinstance(part, int):
            parts.append(f"[{part}]")
        else:
            parts.append(("." if parts else "") + str(part))
    return "".join(parts)


def _describe(error: ValidationError, lang: str) -> tuple[str, str]:
    """Return (field, readable message) for a schema error."""
    field = _path(error)
    v = error.validator
    if v == "required":
        name = error.message.split("'")[1] if "'" in error.message else error.message
        return (f"{field}.{name}" if field else name), word("required", lang, name=name)
    if v == "additionalProperties":
        extra = sorted(set(error.instance) - set(error.schema.get("properties", {})))
        name = ", ".join(extra)
        return (f"{field}.{name}" if field else name), word("unknown", lang, name=name)
    if v == "enum":
        return field, word(
            "enum", lang, value=error.instance, options=", ".join(map(str, error.validator_value))
        )
    if v == "type":
        return field, word("type", lang, expected=error.validator_value)
    if v in ("minimum", "maximum"):
        return field, word("range", lang)
    if v == "pattern":
        return field, word("pattern", lang, value=error.instance)
    if v in ("minLength", "minItems"):
        return field, word("empty", lang)
    if v == "uniqueItems":
        return field, word("duplicate", lang)
    return field, error.message


def _schema_findings(validator: Draft202012Validator, doc, lang: str, op_id: str) -> list[Finding]:
    findings = []
    for error in sorted(validator.iter_errors(doc.data), key=lambda e: list(e.absolute_path)):
        field, text = _describe(error, lang)
        findings.append(Finding(ERROR, "S001", doc.path, field, msg("S001", lang, detail=text), op_id))
    return findings


def check_operation(op: dict, file: str, lang: str = "pt") -> list[Finding]:
    """Business rules for one operation that already passed the schema."""
    op_id = op.get("id", "")
    out: list[Finding] = []

    def add(level: str, code: str, field: str, **kwargs: object) -> None:
        out.append(Finding(level, code, file, field, msg(code, lang, **kwargs), op_id))

    sensitive = op.get("sensitive_data") or []
    if sensitive and not op.get("sensitive_legal_basis"):
        add(ERROR, "R001", "sensitive_legal_basis", categories=", ".join(sensitive))
    if op.get("sensitive_legal_basis") and not sensitive:
        add(WARNING, "R011", "sensitive_legal_basis")

    if op.get("legal_basis") == "legitimate_interest":
        lia = op.get("lia") or {}
        if not lia.get("date"):
            add(ERROR, "R002", "lia")
        elif lia.get("outcome") == "rejected":
            add(ERROR, "R003", "lia.outcome")

    if not (op.get("retention") or {}).get("period", "").strip():
        add(ERROR, "R004", "retention.period")

    for i, transfer in enumerate(op.get("international_transfers") or []):
        if not transfer.get("mechanism"):
            add(ERROR, "R005", f"international_transfers[{i}].mechanism", country=transfer["country"])

    for i, proc in enumerate(op.get("processors") or []):
        missing = [word(k, lang) for k in ("contract", "dpa") if not proc.get(k)]
        if missing:
            add(
                WARNING,
                "R006",
                f"processors[{i}]",
                name=proc["name"],
                missing=word("and", lang).join(missing),
            )

    if not op.get("security_measures"):
        add(WARNING, "R008", "security_measures")

    reasons = dpia_reasons(op, lang)
    if reasons and (op.get("dpia") or {}).get("status") != "done":
        add(WARNING, "R007", "dpia", reason=", ".join(reasons))
    return out


def validate(inventory: Inventory, lang: str = "pt") -> list[Finding]:
    schema = load_schema()
    org_validator = Draft202012Validator({**schema["organization"], "$defs": schema["$defs"]})
    op_validator = Draft202012Validator({**schema["operation"], "$defs": schema["$defs"]})
    findings: list[Finding] = []

    def structural(doc, validator, op_id: str = "") -> bool:
        if doc.error:
            findings.append(Finding(ERROR, "Y001", doc.path, "", msg("Y001", lang, detail=doc.error)))
            return False
        if not isinstance(doc.data, dict):
            findings.append(Finding(ERROR, "Y002", doc.path, "", msg("Y002", lang)))
            return False
        errors = _schema_findings(validator, doc, lang, op_id)
        findings.extend(errors)
        return not errors

    if structural(inventory.organization, org_validator):
        dpo = inventory.org.get("dpo") or {}
        if not (dpo.get("email") or dpo.get("channel")):
            findings.append(Finding(WARNING, "R010", inventory.organization.path, "dpo", msg("R010", lang)))

    if not inventory.operations:
        findings.append(Finding(WARNING, "R012", "operations/", "", msg("R012", lang)))

    seen: dict[str, str] = {}
    for doc in inventory.operations:
        op_id = doc.data.get("id", "") if isinstance(doc.data, dict) else ""
        op_id = op_id if isinstance(op_id, str) else ""
        if not structural(doc, op_validator, op_id):
            continue
        if op_id in seen:
            findings.append(
                Finding(ERROR, "R009", doc.path, "id", msg("R009", lang, id=op_id, other=seen[op_id]), op_id)
            )
        else:
            seen[op_id] = doc.path
        findings.extend(check_operation(doc.data, doc.path, lang))
    return findings


def has_errors(findings: list[Finding]) -> bool:
    return any(f.level == ERROR for f in findings)
