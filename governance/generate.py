"""Generate Weaver registry and human catalog from one source of truth."""
import argparse
import json
from pathlib import Path


def artifacts(c):
    groups = []
    lines = ["# Metrics catalog", "", f"Contract version: {c['version']}", "",
             "Generated from `catalog/metrics.json`; do not edit manually.", "",
             "Required resource attributes: " + ", ".join(c["required_resources"]), ""]
    for m in c["metrics"]:
        groups.append({"id": "metric." + m["name"], "type": "metric", "metric_name": m["name"],
                       "brief": m["description"], "instrument": m["instrument"], "unit": m["unit"],
                       "stability": m["stability"], "attributes": [
                           {"id": k, "type": "string", "stability": "development", "brief": k + " bounded dimension.",
                            "examples": v, "requirement_level": "required"} for k, v in m["attributes"].items()]})
        lines += [f"## `{m['name']}`", "", m["description"], "",
                  f"- Instrument: {m['instrument']}; unit: `{m['unit']}`",
                  f"- Owner: {m['owner']}; stability: {m['stability']}",
                  f"- Dimension combinations per resource: at most {m['max_attribute_combinations']}",
                  f"- Deprecation: {m['deprecation_policy']}"]
        lines += [f"- `{k}`: {', '.join(v)}" for k, v in m["attributes"].items()]
        lines += [""]
    return {"registry/metrics.yaml": json.dumps({"groups": groups}, indent=2) + "\n",
            "docs/catalog.md": "\n".join(lines) + "\n"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    c = json.loads(Path("catalog/metrics.json").read_text())
    for name, text in artifacts(c).items():
        path = Path(name)
        if a.check:
            if not path.exists() or path.read_text() != text:
                raise SystemExit(f"Stale generated file: {name}; run python -m governance.generate")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)


if __name__ == "__main__":
    main()
