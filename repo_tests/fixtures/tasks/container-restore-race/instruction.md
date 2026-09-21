The restore simulator under `/app` looks healthy right after migration, then drifts under delayed replay pressure and can revive retired handles. Repair the runtime so behavior stays stable across restart boundaries, delayed catchup, and repeated sweep calls.

Your fix is complete when the generated report at `/app/output/report.json` consistently reflects a healthy steady run and a healthy delayed-pressure run: no late regression, no retired-handle resurrection, idempotent repeated-run behavior, and healthy lanes in both tracks. Keep the report deterministic across repeated runs.
