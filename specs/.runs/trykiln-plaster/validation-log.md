# Validation Log: trykiln-plaster

## Attempt 1
- Derived score: 14 FAILs, 0 WARNs
- Evidence: specs/.runs/trykiln-plaster/attempt-1-evidence.json
- Evidence errors:
  - naming_pass.instruction_nouns_extracted disagrees with construction_manifest.code_forbidden_tokens (extra in nouns: ['assay', 'attempt_slot', 'impress', 'plaster', 'schema_version', 'spill']; extra in tokens: ['clone', 'migrate', 'stale', 'template']).
  - test name 'test_mold_vat_has_attempt_slot' contains forbidden instruction noun 'attempt_slot'.
  - test name 'test_worker_vat_has_attempt_slot' contains forbidden instruction noun 'attempt_slot'.
  - test name 'test_stale_spill_rejected_nonzero' contains forbidden instruction noun 'spill'.
  - test name 'test_stale_spill_leaves_worker_untouched' contains forbidden instruction noun 'spill'.
  - test name 'test_holdout_extra_migration_rejects_spill' contains forbidden instruction noun 'spill'.
  - test name 'test_zz_recover_corrupt_worker_spill' contains forbidden instruction noun 'spill'.
  - test name 'test_assay_ok_marker_present' contains forbidden instruction noun 'assay'.
  - test name 'test_assay_prints_schema_version' contains forbidden instruction noun 'schema_version'.
  - test name 'test_assay_prints_schema_version' contains forbidden instruction noun 'assay'.
  - test name 'test_schema_version_matches_migration_head' contains forbidden instruction noun 'schema_version'.
  - test name 'test_assay_rerun_consistency' contains forbidden instruction noun 'assay'.
  - test name 'test_assay_exit_zero' contains forbidden instruction noun 'assay'.
  - naming_pass.concentration_math disagrees with computed values: location 'A' ratio supplied=0.3077 computed=0.307692; location 'B' ratio supplied=0.3077 computed=0.307692; location 'C' ratio supplied=0.3846 computed=0.384615
- Blocking evidence failures:
  - naming_pass.instruction_nouns_extracted disagrees with construction_manifest.code_forbidden_tokens (extra in nouns: ['assay', 'attempt_slot', 'impress', 'plaster', 'schema_version', 'spill']; extra in tokens: ['clone', 'migrate', 'stale', 'template']).
  - test name 'test_mold_vat_has_attempt_slot' contains forbidden instruction noun 'attempt_slot'.
  - test name 'test_worker_vat_has_attempt_slot' contains forbidden instruction noun 'attempt_slot'.
  - test name 'test_stale_spill_rejected_nonzero' contains forbidden instruction noun 'spill'.
  - test name 'test_stale_spill_leaves_worker_untouched' contains forbidden instruction noun 'spill'.
  - test name 'test_holdout_extra_migration_rejects_spill' contains forbidden instruction noun 'spill'.
  - test name 'test_zz_recover_corrupt_worker_spill' contains forbidden instruction noun 'spill'.
  - test name 'test_assay_ok_marker_present' contains forbidden instruction noun 'assay'.
  - test name 'test_assay_prints_schema_version' contains forbidden instruction noun 'schema_version'.
  - test name 'test_assay_prints_schema_version' contains forbidden instruction noun 'assay'.
  - test name 'test_schema_version_matches_migration_head' contains forbidden instruction noun 'schema_version'.
  - test name 'test_assay_rerun_consistency' contains forbidden instruction noun 'assay'.
  - test name 'test_assay_exit_zero' contains forbidden instruction noun 'assay'.
  - naming_pass.concentration_math disagrees with computed values: location 'A' ratio supplied=0.3077 computed=0.307692; location 'B' ratio supplied=0.3077 computed=0.307692; location 'C' ratio supplied=0.3846 computed=0.384615

## Attempt 2
- Derived score: 0 FAILs, 0 WARNs
- Evidence: specs/.runs/trykiln-plaster/attempt-2-evidence.json

