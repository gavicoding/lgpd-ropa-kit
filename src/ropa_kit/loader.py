"""Read an inventory folder: ``organization.yaml`` plus ``operations/*.yaml``."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import yaml


class _Loader(yaml.SafeLoader):
    """SafeLoader that keeps dates as plain strings, so ``2026-05-10`` stays ``"2026-05-10"``."""


_Loader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


class InventoryError(Exception):
    """The folder cannot be read as an inventory at all."""


@dataclass
class Document:
    path: str  # relative to the inventory folder, with forward slashes
    data: Any = None
    error: str = ""  # YAML syntax error, if any


@dataclass
class Inventory:
    root: Path
    organization: Document
    operations: list[Document] = field(default_factory=list)

    @property
    def valid_operations(self) -> list[dict]:
        return [d.data for d in self.operations if isinstance(d.data, dict)]

    @property
    def org(self) -> dict:
        return self.organization.data if isinstance(self.organization.data, dict) else {}


def load_schema() -> dict:
    text = resources.files("ropa_kit").joinpath("ropa.schema.json").read_text(encoding="utf-8")
    return json.loads(text)


def _read(root: Path, path: Path) -> Document:
    rel = path.relative_to(root).as_posix()
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_Loader)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" (line {mark.line + 1})" if mark is not None else ""
        return Document(rel, None, f"{getattr(exc, 'problem', None) or exc}{where}")
    except UnicodeDecodeError:
        return Document(rel, None, "file is not UTF-8")
    except OSError as exc:
        # permission denied, file locked by a sync client, a folder named like *.yaml...
        return Document(rel, None, f"cannot read file: {exc.strerror or exc}")
    return Document(rel, data)


def load_inventory(folder: str | Path) -> Inventory:
    root = Path(folder)
    if not root.is_dir():
        raise InventoryError(f"folder not found: {root}")
    org_path = next((p for p in (root / "organization.yaml", root / "organization.yml") if p.is_file()), None)
    if org_path is None:
        raise InventoryError(f"{root} has no organization.yaml")
    ops_dir = root / "operations"
    files = sorted([*ops_dir.glob("*.yaml"), *ops_dir.glob("*.yml")]) if ops_dir.is_dir() else []
    return Inventory(root, _read(root, org_path), [_read(root, p) for p in files])
