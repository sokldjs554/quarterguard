"""Dated evidence summary; historical evaluation artifacts remain unchanged."""
import hashlib
import json
from .store import ROOT


def load_latest_progress():
    summary = json.loads((ROOT/'data/latest-progress-period-diagnostic-20261110.json').read_text())
    if summary.get('schema_version') != 1 or not summary.get('source_sha256'):
        raise ValueError('SUMMARY_SCHEMA_MISMATCH')
    for name, expected in summary['source_sha256'].items():
        path = (ROOT/name).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError('SUMMARY_SOURCE_MISMATCH')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('SUMMARY_SOURCE_MISMATCH')
    return summary
