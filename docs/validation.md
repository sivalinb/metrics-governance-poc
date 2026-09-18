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

Docker is unavailable on the authoring machine. The GitHub Actions integration test successfully built and ran the demo, Collector, and Prometheus, and verified translated operation counters for both services through the real Prometheus API. The first governance run exposed an incorrect Linux Weaver archive suffix; the installer was corrected to use the official `x86_64-unknown-linux-gnu` release asset. See repository Actions for the latest complete run.

The smoke test checks connectivity, translation of the operation counter, and service identity. It does not exhaustively test all metric translations, histogram bucket behavior, restart handling, or production load.

## Deliberate limits

This POC implements catalog and CI governance. It does not configure branch protections, add Grafana dashboards, enforce historical compatibility/deprecation deadlines, run a live cardinality monitor, or provide production SLO alerts. The README and guide explain follow-on work.
