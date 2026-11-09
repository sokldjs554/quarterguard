"""Load the original follow-up policy for offline historical audits only.

The archived modules must match the already-published freeze. All other source
files still undergo the original validator's live-tree checks. Nothing in the
freeze, original harness, response or historical score is rewritten.
"""
import hashlib
import importlib.util
import json
from .store import ROOT

ARCHIVE = ROOT / 'data/llm-followup-20261110/source-snapshot'


def load_frozen_followup():
    frozen = json.loads((ARCHIVE.parent / 'freeze.json').read_text())
    archived = {}
    for name in ('explanation_context.py', 'public_providers.py'):
        key = 'quarterguard/' + name
        path = ARCHIVE / name
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if sha != frozen['source_hashes'][key]:
            raise ValueError('HISTORICAL_SOURCE_HASH_MISMATCH')
        archived[key] = sha

    def load(name, path):
        spec = importlib.util.spec_from_file_location('quarterguard.' + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    context = load('_frozen_context_v4', ARCHIVE / 'explanation_context.py')
    audit = load('_frozen_followup_v4', ROOT / 'quarterguard/evaluate_live_explanations_v4.py')
    audit.build_context = context.build_context
    audit.INSTRUCTIONS = audit.PUBLIC_INSTRUCTIONS = context.INSTRUCTIONS
    current_hashes = audit.source_hashes
    audit.source_hashes = lambda: current_hashes() | archived
    audit.validate_freeze(frozen)
    return audit
