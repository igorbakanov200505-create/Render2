#!/usr/bin/env python3
"""Server-side public HTTP reachability monitor; no authentication or personal data."""
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / 'monitor' / 'config.json'
STATUS_FILE = ROOT / 'data' / 'status.json'


def read_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, OSError):
        return fallback


def run_check(url, timeout, expected):
    start = time.monotonic()
    request = urllib.request.Request(
        url,
        headers={'User-Agent': 'UiirmeHub-Pulse/3.0 (+GitHub Actions)', 'Accept': 'text/html,application/json,*/*'},
        method='GET',
    )
    status_code = None
    error = None
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context()) as resp:
            status_code = resp.status
            # HTTP headers and status are enough to test public reachability.
            # Do not store response bodies; they could contain private data.
    except urllib.error.HTTPError as exc:
        status_code = exc.code
        error = f'HTTP {exc.code}'
    except urllib.error.URLError as exc:
        error = f'Ошибка соединения ({type(exc.reason).__name__})'
    except (TimeoutError, OSError, ValueError) as exc:
        error = f'Ошибка проверки ({type(exc).__name__})'
    duration_ms = int((time.monotonic() - start) * 1000)
    ok = status_code in expected
    if not ok and not error:
        error = f'Неожиданный HTTP {status_code}' if status_code is not None else 'Нет ответа сервера'
    return {
        'checked_at': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'status': 'up' if ok else 'down',
        'http_status': status_code,
        'duration_ms': duration_ms,
        'error': None if ok else error,
    }


def main():
    cfg = read_json(CONFIG_FILE, {})
    url = cfg.get('target_url', '')
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise SystemExit('monitor/config.json: требуется безопасный HTTPS-адрес без учетных данных')
    timeout = max(3, min(60, int(cfg.get('timeout_seconds', 35))))
    max_history = max(10, min(1000, int(cfg.get('max_history', 288))))
    expected = set(int(s) for s in cfg.get('expected_http_status', [200]))
    current = read_json(STATUS_FILE, {})
    previous = current.get('history', []) if isinstance(current.get('history'), list) else []
    sample = run_check(url, timeout, expected)
    history = [entry for entry in previous if isinstance(entry, dict)][-(max_history - 1):] + [sample]
    counts = current.get('counts', {})
    result = {
        'schema_version': 1,
        **sample,
        'counts': {
            'total': int(counts.get('total', 0)) + 1,
            'success': int(counts.get('success', 0)) + int(sample['status'] == 'up'),
            'error': int(counts.get('error', 0)) + int(sample['status'] != 'up'),
        },
        'history': history,
    }
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATUS_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, STATUS_FILE)
    print(json.dumps({'status': sample['status'], 'http_status': sample['http_status'], 'duration_ms': sample['duration_ms']}, ensure_ascii=False))
    # Intentional exit 0 for HTTP failures: the result must still be published to Pages.
    return 0


if __name__ == '__main__':
    sys.exit(main())
