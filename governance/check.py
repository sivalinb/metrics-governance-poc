"""Fail-closed checks for the organization contract and SDK-emitted OTLP JSON."""
import argparse
import json
import re
from pathlib import Path


def check_catalog(c):
    errors = []
    if not re.fullmatch(r"\d+\.\d+\.\d+", c.get("version", "")):
        errors.append("catalog: version must be semantic version")
    if not c.get("required_resources"):
        errors.append("catalog: required_resources cannot be empty")
    seen = set()
    for m in c.get("metrics", []):
        n = m.get("name", "")
        if n in seen:
            errors.append(f"{n}: duplicate name")
        seen.add(n)
        if not re.fullmatch(r"demo\.[a-z][a-z0-9_.]*", n):
            errors.append(f"{n}: use the demo namespace")
        for k in ("owner", "description", "deprecation_policy"):
            if not str(m.get(k, "")).strip():
                errors.append(f"{n}: missing {k}")
        if m.get("instrument") not in ("counter", "histogram"):
            errors.append(f"{n}: unsupported instrument")
        if m.get("unit") not in ("s", "USD", "{operation}", "{order}", "{error}"):
            errors.append(f"{n}: unapproved unit")
        product = 1
        for key, values in m.get("attributes", {}).items():
            if not key.startswith("demo.") or not values or len(set(values)) != len(values):
                errors.append(f"{n}: invalid attribute domain {key}")
            product *= len(values)
        if not m.get("attributes") or product > m.get("max_attribute_combinations", 0):
            errors.append(f"{n}: attribute budget exceeded or missing")
    if not seen:
        errors.append("catalog: no metrics")
    return errors


def attrs(items):
    return {a["key"]: next(iter(a["value"].values())) for a in items}


def check_telemetry(c, payload):
    errors = []
    definitions = {m["name"]: m for m in c["metrics"]}
    coverage = {}
    for rm in payload.get("resourceMetrics", []):
        resource = attrs(rm.get("resource", {}).get("attributes", []))
        service = resource.get("service.name", "<missing>")
        for key in c["required_resources"]:
            if not resource.get(key):
                errors.append(f"{service}: missing resource {key}")
        coverage.setdefault(service, set())
        for sm in rm.get("scopeMetrics", []):
            for metric in sm.get("metrics", []):
                n = metric.get("name", "")
                if n not in definitions:
                    errors.append(f"{service}/{n}: unknown metric")
                    continue
                m = definitions[n]
                coverage[service].add(n)
                if metric.get("unit") != m["unit"]:
                    errors.append(f"{n}: wrong unit {metric.get('unit')!r}; expected {m['unit']!r}")
                key = "sum" if m["instrument"] == "counter" else "histogram"
                data = metric.get(key)
                if data is None:
                    errors.append(f"{n}: wrong instrument; expected {key}")
                    continue
                if key == "sum" and not data.get("isMonotonic"):
                    errors.append(f"{n}: counter must be monotonic")
                if data.get("aggregationTemporality") not in (2, "AGGREGATION_TEMPORALITY_CUMULATIVE"):
                    errors.append(f"{n}: expected cumulative temporality")
                points = data.get("dataPoints", [])
                if not points:
                    errors.append(f"{n}: no data points")
                for point in points:
                    labels = attrs(point.get("attributes", []))
                    if set(labels) != set(m["attributes"]):
                        errors.append(f"{n}: unapproved or missing attributes: {sorted(labels)}")
                    for label, value in labels.items():
                        if label in m["attributes"] and value not in m["attributes"][label]:
                            errors.append(f"{n}: unapproved value for {label}: {value!r}")
    if not coverage:
        errors.append("telemetry: empty capture")
    for service, names in coverage.items():
        for missing in sorted(set(definitions) - names):
            errors.append(f"{service}: missing metric {missing}")
    return errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", default="catalog/metrics.json")
    p.add_argument("--telemetry")
    args = p.parse_args()
    c = json.loads(Path(args.catalog).read_text())
    errors = check_catalog(c)
    if args.telemetry:
        errors += check_telemetry(c, json.loads(Path(args.telemetry).read_text()))
    for error in errors:
        print("ERROR:", error)
    if errors:
        raise SystemExit(1)
    print("PASS: metrics governance checks")


if __name__ == "__main__":
    main()
