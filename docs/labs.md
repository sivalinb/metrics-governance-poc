# Learning exercises

Run from the repository root with the virtual environment active. Suggested times are rough hands-on estimates, excluding installation.

## Lab 1: Inspect a metric contract (20 minutes)

Read `catalog/metrics.json` and `docs/catalog.md`. Explain why duration uses seconds, why ownership is metadata rather than a metric label, and why counting both checkout and payment orders is not a deduplicated business total.

Run `python -m governance.check` and `python -m governance.generate --check`.

**Success:** all five definitions are valid and generated artifacts match their source.

## Lab 2: Reject telemetry drift (30 minutes)

Run the valid emission/check commands in the README. Inspect `build/telemetry.json`: find the two service resources, metric units, sum monotonicity, histogram buckets, and attributes.

Run each intentional violation separately. Confirm the checker exits with status 1 (`echo $?` immediately after the check). The unit case changes the emitted metadata to `ms`; the attribute case introduces synthetic customer IDs.

**Success:** valid telemetry passes and both bad captures fail for the intended reason.

## Lab 3: Reject a governance violation (20 minutes)

Temporarily remove one metric's `owner` from the catalog. Run the catalog checker and observe `missing owner`. Restore the field. Change only a description without regenerating: the generated-artifact check should fail. Run the generator, inspect the diff, then restore or commit your intended change.

**Success:** missing ownership and stale documentation cannot quietly pass CI.

## Lab 4: Observe the complete pipeline (30 minutes)

Start Compose. Inspect the Collector `/metrics` endpoint and query Prometheus using the guide. Observe cumulative counters increasing every ten seconds. Compare OTel names against translated Prometheus names and locate `service_name`.

**Success:** both checkout and payment have metrics; error ratio approaches 20% after a suitable rate window.

## Lab 5: Use Weaver live-check as an additional diagnostic (20 minutes)

After generating `build/telemetry.json`, run:

```bash
python -m governance.weaver_samples build/telemetry.json build/weaver-samples.json
.tools/weaver registry live-check -r registry   --input-source build/weaver-samples.json --input-format json   --format json --output build/weaver-live
```

Inspect the generated report. Weaver v0.19 file input expects an array of sample entities, not a raw OTLP request; the adapter converts actual SDK-emitted metrics into that format. Resource attributes are deliberately excluded from this metric-only adapter and validated by the Python policy checker.

Repeat with `build/bad-unit.json` or `build/bad-attribute.json` as adapter input and observe Weaver's violations and nonzero exit status. The CI workflow checks valid samples using both tools. The Python checker additionally enforces ownership, finite attribute values, resource requirements, and coverage.

**Success:** you can explain a registry validation result, a telemetry conformance finding, and a CI-blocking policy failure.

## Follow-on projects

- Add automatic comparison against the main-branch contract for breaking changes.
- Add SDK Views and benchmark cardinality before/after dimension filtering.
- Add a Prometheus integration test that snapshots expected names after translation.
- Standardize latency bucket boundaries and test SLO recording/alerting rules with promtool.
- Generate a browsable catalog and add real team ownership/review rules.
