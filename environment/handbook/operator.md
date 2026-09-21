# Quench roster handbook

## Job documents

Each job YAML file declares an `aim` field naming which ledger targets to roster.

Accepted writings for `aim`:

- A YAML sequence of target name strings.
- A bare YAML string naming a single target, when only one target is wanted.

Both writings are supported. A bare string is a convenience for the single-target case; it is not a different product mode.

Target names are opaque strings. A comma character inside a name is part of the name. Do not treat commas as list separators inside a bare string.

## Ledger

Registered targets and their dependency edges live in `/app/ledger/targets.toml`.

## Roster output

`quench roster` writes a JSON sheet with `picked`, `missing`, and `aim_kind`.

## Name characters

Ledger target names may contain commas. A bare YAML string containing a comma is still one name (for example `lib,core`).
