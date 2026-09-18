"""Two synthetic services, real OTel SDK instruments and OTLP encoding."""
import argparse
import json
import time
from pathlib import Path
from google.protobuf.json_format import MessageToDict
from opentelemetry.exporter.otlp.proto.common.metrics_encoder import encode_metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.resources import Resource


class DemoService:
    def __init__(self, service, violation=None):
        self.service = service
        self.violation = violation
        self.reader = InMemoryMetricReader()
        self.provider = MeterProvider(metric_readers=[self.reader], resource=Resource.create({
            "service.name": service, "service.version": "1.0.0",
            "deployment.environment.name": "poc"}))
        meter = self.provider.get_meter("metrics-governance-demo", "1.0.0")
        # Independent of the catalog so validation detects instrumentation drift.
        self.count = meter.create_counter("demo.operation.count", unit="{operation}")
        self.duration = meter.create_histogram("demo.operation.duration", unit="ms" if violation == "unit" else "s")
        self.errors = meter.create_counter("demo.operation.errors", unit="{error}")
        self.orders = meter.create_counter("demo.order.count", unit="{order}")
        self.value = meter.create_histogram("demo.order.value", unit="USD")

    def collect(self):
        for i in range(20):
            failed = i % 5 == 0
            labels = {"demo.operation": "checkout" if self.service == "checkout" else "payment",
                      "demo.outcome": "failure" if failed else "success"}
            if self.violation == "attribute":
                labels["demo.customer_id"] = f"synthetic-{i}"
            self.count.add(1, labels)
            self.duration.record(0.05 + i / 100, labels)
            if failed:
                self.errors.add(1, labels)
            else:
                self.orders.add(1, labels)
                self.value.record(19.99, labels)
        return self.reader.get_metrics_data()

    def shutdown(self):
        self.provider.shutdown()


def capture(service, violation=None):
    demo = DemoService(service, violation)
    try:
        return demo.collect()
    finally:
        demo.shutdown()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="build/telemetry.json")
    p.add_argument("--violation", choices=["unit", "attribute"])
    p.add_argument("--endpoint", help="Full OTLP HTTP metrics URL")
    p.add_argument("--loop", action="store_true")
    a = p.parse_args()
    exporter = OTLPMetricExporter(endpoint=a.endpoint) if a.endpoint else None
    services = [DemoService(name, a.violation) for name in ("checkout", "payment")]
    try:
        while True:
            payload = {"resourceMetrics": []}
            for service in services:
                data = service.collect()
                payload["resourceMetrics"].extend(MessageToDict(encode_metrics(data))["resourceMetrics"])
                if exporter:
                    result = exporter.export(data)
                    if result.name != "SUCCESS":
                        raise RuntimeError(f"OTLP export failed: {result}")
            path = Path(a.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2) + "\n")
            print(f"Captured two services to {path}", flush=True)
            if not a.loop:
                break
            time.sleep(10)
    finally:
        for service in services:
            service.shutdown()
        if exporter:
            exporter.shutdown()


if __name__ == "__main__":
    main()
