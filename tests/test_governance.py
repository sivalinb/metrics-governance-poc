import copy
import json
from pathlib import Path
import pytest
from google.protobuf.json_format import MessageToDict
from opentelemetry.exporter.otlp.proto.common.metrics_encoder import encode_metrics
from demo.emit import capture
from governance.check import check_catalog, check_telemetry


@pytest.fixture
def catalog():
    return json.loads(Path("catalog/metrics.json").read_text())


def payload(violation=None):
    result = {"resourceMetrics": []}
    for service in ("checkout", "payment"):
        result["resourceMetrics"].extend(MessageToDict(encode_metrics(capture(service, violation)))["resourceMetrics"])
    return result


def test_valid_real_sdk_telemetry(catalog):
    assert check_catalog(catalog) == []
    assert check_telemetry(catalog, payload()) == []


@pytest.mark.parametrize("violation,expected", [("unit", "wrong unit"), ("attribute", "unapproved or missing attributes")])
def test_instrumentation_drift(catalog, violation, expected):
    assert any(expected in e for e in check_telemetry(catalog, payload(violation)))


@pytest.mark.parametrize("mutation,expected", [
    (lambda c: c["metrics"][0].pop("owner"), "missing owner"),
    (lambda c: c["metrics"].append(copy.deepcopy(c["metrics"][0])), "duplicate name"),
    (lambda c: c["metrics"][0].update(max_attribute_combinations=1), "budget exceeded"),
])
def test_contract_violations(catalog, mutation, expected):
    mutation(catalog)
    assert any(expected in e for e in check_catalog(catalog))


def test_empty_capture_rejected(catalog):
    assert check_telemetry(catalog, {}) == ["telemetry: empty capture"]


def test_missing_resource_and_metric(catalog):
    p = payload()
    p["resourceMetrics"][0]["resource"]["attributes"] = []
    p["resourceMetrics"][0]["scopeMetrics"][0]["metrics"].pop()
    errors = check_telemetry(catalog, p)
    assert any("missing resource service.name" in e for e in errors)
    assert any("missing metric" in e for e in errors)


def test_unknown_metric_and_bad_counter(catalog):
    p = payload()
    metrics = p["resourceMetrics"][0]["scopeMetrics"][0]["metrics"]
    metrics.append({"name": "rogue.metric"})
    next(m for m in metrics if m["name"] == "demo.operation.count")["sum"]["isMonotonic"] = False
    errors = check_telemetry(catalog, p)
    assert any("unknown metric" in e for e in errors)
    assert any("monotonic" in e for e in errors)


def test_repeated_collection_preserves_cumulative_counters():
    from demo.emit import DemoService
    service = DemoService('checkout')
    try:
        values = []
        for _ in range(2):
            p = MessageToDict(encode_metrics(service.collect()))
            metrics = p['resourceMetrics'][0]['scopeMetrics'][0]['metrics']
            counter = next(m for m in metrics if m['name'] == 'demo.operation.count')
            values.append(sum(int(p['asInt']) for p in counter['sum']['dataPoints']))
        assert values == [20, 40]
    finally:
        service.shutdown()


def test_weaver_adapter_preserves_observed_unit_and_attributes():
    from governance.weaver_samples import convert
    samples = convert(payload('unit'))
    durations = [s['metric'] for s in samples if s['metric']['name'] == 'demo.operation.duration']
    assert len(durations) == 2
    assert all(m['unit'] == 'ms' for m in durations)
    samples = convert(payload('attribute'))
    assert any(a['name'] == 'demo.customer_id' for s in samples for p in s['metric']['data_points'] for a in p['attributes'])
