# Metrics governance POC

A hands-on lab for defining a metrics contract and enforcing it in CI using **OpenTelemetry, Weaver, and Prometheus**.

Two synthetic services (`checkout` and `payment`) emit five real OpenTelemetry SDK metrics. A versioned catalog defines their meaning, units, dimensions, ownership, and lifecycle. Weaver validates the generated semantic convention registry; organization-specific checks validate actual SDK-emitted OTLP JSON and fail CI on drift.

## Quick start: no Docker required

Use Python 3.12 (recommended), Git, and an internet connection for installation. Run commands from the repository root.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m governance.check
python -m governance.generate --check
python -m pytest -q
python -m demo.emit
python -m governance.check --telemetry build/telemetry.json
bash scripts/install-weaver.sh
.tools/weaver registry check -r registry
```

Expected: tests pass, the telemetry check prints `PASS`, and Weaver reports a valid registry.

## Prove that governance works

```bash
python -m demo.emit --violation unit --output build/bad-unit.json
python -m governance.check --telemetry build/bad-unit.json
# Expected exit 1: demo.operation.duration uses ms instead of s.

python -m demo.emit --violation attribute --output build/bad-attribute.json
python -m governance.check --telemetry build/bad-attribute.json
# Expected exit 1: demo.customer_id is not an approved dimension.
```

These commands intentionally fail. The GitHub Actions workflow asserts that both violations are rejected.

## Run the complete pipeline

Install Docker with Compose v2, then:

```bash
docker compose up --build -d
curl -fsS http://localhost:8889/metrics
# Open http://localhost:9090 and run:
# sum by (service_name) (demo_operation_count_total)
docker compose logs --tail=50 demo collector
docker compose down
```

Allow 15–30 seconds for export and scraping. The demo generates a batch of 20 operations per service every 10 seconds, with 20% failures. Counters remain cumulative across batches. This is a synthetic instrumentation workload, not an HTTP application.

Only loopback ports are published. The Collector adds the approved `service.name` resource as a label for Prometheus; it does not promote every resource attribute.

## Read next

- [Detailed architecture, governance, and operations guide](docs/guide.md)
- [Generated metrics catalog](docs/catalog.md)
- [Step-by-step learning exercises](docs/labs.md)
- [Validation results and known limits](docs/validation.md)

## Repository map

| Path | Purpose |
|---|---|
| `catalog/metrics.json` | Authoritative organization contract |
| `registry/metrics.yaml` | Generated Weaver registry (JSON is valid YAML) |
| `governance/` | Contract validation, telemetry checks, documentation generation |
| `demo/emit.py` | Two service resources using the real OTel Python SDK |
| `tests/` | Positive and adversarial governance tests |
| `config/` | Collector and Prometheus configuration |
| `.github/workflows/governance.yml` | Automated validation and capture artifacts |

The scope implements the first two recommended POCs: a catalog and CI enforcement. Cardinality budgeting is introductory; full runtime cardinality monitoring, SLO alerting, and Grafana dashboards are future exercises.
