# Validation record

## Locally verified

- Real OTel Python SDK emission and official OTLP protobuf-to-JSON encoding for two service resources.
- Positive telemetry passes the organization policy checker.
- Incorrect duration units and unexpected synthetic customer IDs fail both the policy checker and Weaver live-check.
- Weaver v0.19.0 registry validation succeeds without warnings.
- Weaver v0.19.0 live-check accepts metric samples adapted from the valid SDK capture.
- Generated registry and Markdown match the authoritative catalog.
- Automated tests cover valid telemetry, drift, missing ownership, duplicate definitions, dimension budgets, empty captures, missing resource/metric data, unknown metrics, nonmonotonic counters, cumulative collection, and adapter fidelity.

Local tests used Python 3.9.6 on Apple Silicon. Its system LibreSSL produces an urllib3 warning; offline telemetry tests pass. Python 3.12 is the recommended environment and the CI target.

## Container verification

Docker is unavailable on the authoring machine. Compose execution is therefore delegated to the included GitHub Actions `integration` job, which builds the demo, starts Collector and Prometheus, and polls the real Prometheus query API until translated counters from both services are present. Check the repository Actions run for the remote result.

The smoke test checks connectivity, translation of the operation counter, and service identity. It does not exhaustively test all metric translations, histogram bucket behavior, restart handling, or production load.

## Deliberate limits

This POC implements catalog and CI governance. It does not configure branch protections, add Grafana dashboards, enforce historical compatibility/deprecation deadlines, run a live cardinality monitor, or provide production SLO alerts. The README and guide explain follow-on work.
