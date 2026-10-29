import json
from pathlib import Path
from .core import Fact
ROOT=Path(__file__).resolve().parents[1]
def load_facts():
    return [Fact(**{k:v for k,v in row.items() if k!='months'}) for row in json.loads((ROOT/'data/facts.json').read_text())]
