# Engineering Archive

This directory preserves retired engineering scaffolding and historical probe material for provenance.

## Scope

- It is **not** ordinary product runtime source.
- It is **excluded by default** from Chinese software-copyright source selection and user-facing documentation.
- Files here are retained so historical engineering evidence remains reviewable without cluttering active development surfaces.
- Historical tests that only exercise archived probe harnesses are archived beside that scaffolding so the active test suite does not import retired modules.
- Do not treat archived workflows as active GitHub Actions. Historical workflow files are intentionally stored outside `.github/workflows/`.

## Layout

`engineering-scaffolding/` preserves the original repository-relative path beneath the archive root, so provenance is easy to reconstruct.

Current product/runtime code, active tests, packaging, legal/governance files, and still-used maintenance tooling remain in their canonical locations.
