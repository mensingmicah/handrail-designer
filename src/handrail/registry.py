"""The code-value registry: loading, validation, lookup and usage tracking.

CLAUDE.md rule 1 is enforced here, not left to discipline:

- The registry refuses to load if its review list is not exactly the set of
  drafted entries, if an entry is missing a required field, or if an entry
  claims "verified" without the engineer's name and date.
- ``get`` stops with an error naming any entry that does not exist.
- Every entry a calc reads is recorded, so the PDF can list exactly the
  drafted entries that calc used and stamp every page DRAFT.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from handrail.units import Q_

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "registry" / "code-values.toml"

REQUIRED = (
    "id", "value", "unit", "cite", "document", "edition", "section",
    "source", "status", "drafted_on", "verified_by", "verified_date",
)
STATUSES = ("drafted", "verified")
# Units that mark an entry as something other than a physical quantity.
NON_QUANTITY_UNITS = ("text", "list", "equation", "provision", "factors")


class RegistryError(Exception):
    """The registry file is malformed or inconsistent with rule 1."""


class MissingEntry(RegistryError):
    """A calc asked for an entry that does not exist."""


@dataclass(frozen=True)
class Entry:
    id: str
    value: Any
    unit: str
    cite: str       # short citation printed beside each calc line
    document: str
    edition: str
    section: str
    source: str
    status: str
    note: str = ""

    @property
    def drafted(self) -> bool:
        return self.status == "drafted"

    @property
    def quantity(self):
        """The value as a pint quantity (or a plain float if dimensionless)."""
        if self.unit in NON_QUANTITY_UNITS:
            raise RegistryError(f"{self.id} is a {self.unit} entry, not a quantity")
        if self.unit == "":
            return self.value  # int or float, kept as written so it prints as written
        return Q_(self.value, self.unit)


class Registry:
    def __init__(self, path: Path = REGISTRY_PATH):
        self.path = Path(path)
        try:
            with open(self.path, "rb") as f:
                raw = tomllib.load(f)
        except FileNotFoundError:
            raise RegistryError(f"registry file not found: {self.path}") from None
        except tomllib.TOMLDecodeError as e:
            raise RegistryError(f"registry file {self.path} is not valid TOML: {e}") from None
        self.entries: dict[str, Entry] = {}
        self._load(raw)
        self._used: dict[str, None] = {}  # insertion-ordered set

    def _load(self, raw: dict) -> None:
        for i, e in enumerate(raw.get("entry", [])):
            where = e.get("id", f"entry #{i + 1}")
            missing = [k for k in REQUIRED if k not in e]
            if missing:
                raise RegistryError(f"{where}: missing field(s) {', '.join(missing)}")
            if e["status"] not in STATUSES:
                raise RegistryError(f"{where}: status must be one of {STATUSES}, not {e['status']!r}")
            if e["status"] == "verified" and not (e["verified_by"] and e["verified_date"]):
                raise RegistryError(f"{where}: marked verified without verified_by and verified_date")
            if e["status"] == "drafted" and (e["verified_by"] or e["verified_date"]):
                raise RegistryError(f"{where}: drafted entry has verified_by or verified_date filled in")
            if e["id"] in self.entries:
                raise RegistryError(f"{where}: duplicate id")
            self.entries[e["id"]] = Entry(
                id=e["id"], value=e["value"], unit=e["unit"], cite=e["cite"],
                document=e["document"], edition=e["edition"], section=e["section"],
                source=e["source"], status=e["status"], note=e.get("note", ""),
            )

        review = raw.get("review")
        if review is None:
            raise RegistryError("registry has no review list")
        if len(review) != len(set(review)):
            raise RegistryError("review list has duplicate ids")
        drafted = {k for k, v in self.entries.items() if v.drafted}
        if set(review) != drafted:
            not_listed = sorted(drafted - set(review))
            not_drafted = sorted(set(review) - drafted)
            msg = ["review list does not match the drafted entries."]
            if not_listed:
                msg.append(f"Drafted but not in review list: {', '.join(not_listed)}.")
            if not_drafted:
                msg.append(f"In review list but not a drafted entry: {', '.join(not_drafted)}.")
            raise RegistryError(" ".join(msg))
        self.review = list(review)

    def get(self, entry_id: str) -> Entry:
        """Return an entry and record that this calc used it."""
        try:
            entry = self.entries[entry_id]
        except KeyError:
            raise MissingEntry(
                f"The calc needs registry entry {entry_id!r}, which does not exist "
                f"in {self.path.name}. Add it as a drafted entry (CLAUDE.md rule 1)."
            ) from None
        self._used[entry_id] = None
        return entry

    @property
    def used(self) -> list[Entry]:
        return [self.entries[k] for k in self._used]

    @property
    def drafted_used(self) -> list[Entry]:
        return [e for e in self.used if e.drafted]
