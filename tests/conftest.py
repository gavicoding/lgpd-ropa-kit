from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ORG = {
    "controller": {"name": "Empresa Exemplo Ltda", "cnpj": "11.222.333/0001-81"},
    "dpo": {"name": "Encarregado (exemplo)", "email": "privacidade@exemplo.test"},
    "reviewed_at": "2026-11-01",
}


def base_op(**overrides) -> dict:
    """A fully valid operation; tests change one thing at a time."""
    op = {
        "id": "op-teste",
        "name": "Operação de teste",
        "area": "TI",
        "purpose": "Testar o validador.",
        "data_subjects": ["clientes"],
        "personal_data": ["nome", "e-mail"],
        "legal_basis": "contract",
        "retention": {"period": "1 ano"},
        "security_measures": ["Acesso por perfil"],
        "risk": {"likelihood": 1, "impact": 2},
    }
    op.update(overrides)
    return {k: v for k, v in op.items() if v is not None}


@pytest.fixture
def make_inventory(tmp_path: Path):
    counter = iter(range(1000))

    def make(*ops: dict, org: dict | None = None, raw: dict[str, str] | None = None) -> Path:
        root = tmp_path / f"inv{next(counter)}"
        (root / "operations").mkdir(parents=True)
        (root / "organization.yaml").write_text(
            yaml.safe_dump(ORG if org is None else org, allow_unicode=True), encoding="utf-8"
        )
        for i, op in enumerate(ops):
            name = f"{i:02d}-{op.get('id', 'sem-id')}.yaml"
            (root / "operations" / name).write_text(
                yaml.safe_dump(op, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
        for name, text in (raw or {}).items():
            (root / name).write_text(text, encoding="utf-8")
        return root

    return make
