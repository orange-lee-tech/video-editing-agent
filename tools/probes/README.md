# Probe Harnesses

This directory contains reusable Engineering/Product Probe harnesses.

## Evidence rule

**Engineering Probe**: synthetic/controlled fixtures are allowed when proving contracts, algorithms, runtime wiring or negative controls.

**Product Probe**: use real representative inputs when claiming editing usefulness, preference or product quality. Synthetic fixtures must not be presented as product-quality evidence.

## Authority rule

A probe must execute the real owned path it claims to validate.

Forbidden evidence shortcuts include:

- preconstructing the winning candidate/window/source range and then claiming retrieval/resolution selected it;
- hardcoding FFmpeg trim/duck/fade answers that are supposed to come from canonical decisions;
- measuring an input fixture while reporting the metric as final rendered-output QC.

Expected answers may exist separately for scoring/ground truth, but must never be injected as system outputs.

Private inputs and generated previews remain gitignored. Durable conclusions belong in `docs/validation/` or `docs/logs/PROBE_LEDGER.md`, not in committed media.
