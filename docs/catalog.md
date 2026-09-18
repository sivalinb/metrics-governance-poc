# Metrics catalog

Contract version: 1.0.0

Generated from `catalog/metrics.json`; do not edit manually.

Required resource attributes: service.name, service.version, deployment.environment.name

## `demo.operation.count`

Completed operations, including failures.

- Instrument: counter; unit: `{operation}`
- Owner: demo-platform; stability: development
- Dimension combinations per resource: at most 4
- Deprecation: Announce replacement and support both names for at least 30 days before removal.
- `demo.operation`: checkout, payment
- `demo.outcome`: success, failure

## `demo.operation.duration`

Elapsed time of completed operations.

- Instrument: histogram; unit: `s`
- Owner: demo-platform; stability: development
- Dimension combinations per resource: at most 4
- Deprecation: Announce replacement and support both names for at least 30 days before removal.
- `demo.operation`: checkout, payment
- `demo.outcome`: success, failure

## `demo.operation.errors`

Failed operations only; a subset of completed operations.

- Instrument: counter; unit: `{error}`
- Owner: demo-platform; stability: development
- Dimension combinations per resource: at most 4
- Deprecation: Announce replacement and support both names for at least 30 days before removal.
- `demo.operation`: checkout, payment
- `demo.outcome`: success, failure

## `demo.order.count`

Orders successfully accepted during an operation.

- Instrument: counter; unit: `{order}`
- Owner: demo-platform; stability: development
- Dimension combinations per resource: at most 4
- Deprecation: Announce replacement and support both names for at least 30 days before removal.
- `demo.operation`: checkout, payment
- `demo.outcome`: success, failure

## `demo.order.value`

Value of accepted orders in US dollars.

- Instrument: histogram; unit: `USD`
- Owner: demo-platform; stability: development
- Dimension combinations per resource: at most 4
- Deprecation: Announce replacement and support both names for at least 30 days before removal.
- `demo.operation`: checkout, payment
- `demo.outcome`: success, failure

