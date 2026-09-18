"""Poll the real Prometheus API and require metrics from both demo services."""
import json
import time
from urllib.parse import urlencode
from urllib.request import urlopen

query = 'sum by (service_name) (demo_operation_count_total)'
url = 'http://localhost:9090/api/v1/query?' + urlencode({'query': query})
deadline = time.monotonic() + 90
last = 'No response'
while time.monotonic() < deadline:
    try:
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        results = payload['data']['result']
        services = {r['metric'].get('service_name') for r in results if float(r['value'][1]) > 0}
        if {'checkout', 'payment'} <= services:
            print('PASS: Prometheus ingested translated metrics for both services')
            break
        last = repr(payload)
    except Exception as exc:
        last = str(exc)
    time.sleep(3)
else:
    raise SystemExit('Prometheus smoke test failed: ' + last)
