"""dataset.py
Carga y representación del banco de enfermedades.
"""
import json
from pathlib import Path
from typing import Dict, Any, List

class Disease:
    def __init__(self, raw: Dict[str, Any]):
        self.id = raw['id']
        self.name = raw.get('name', raw['id'])
        self.prior = float(raw.get('prior', 0.0))
        self.symptom_likelihood = raw.get('symptom_likelihood', {})
        self.risk_factors = raw.get('risk_factors', {})

    def likelihood(self, symptom: str) -> float:
        # P(symptom | disease)
        return float(self.symptom_likelihood.get(symptom, 0.01))

class Dataset:
    def __init__(self, path: str):
        self.path = Path(path)
        self.diseases = self._load()

    def _load(self) -> List[Disease]:
        with open(self.path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        return [Disease(d) for d in raw.get('diseases', [])]

    def priors(self) -> Dict[str, float]:
        return {d.id: d.prior for d in self.diseases}

    def get_by_id(self, id_: str) -> Disease:
        for d in self.diseases:
            if d.id == id_:
                return d
        raise KeyError(f"Disease {id_} not found")

    def all_symptoms(self) -> List[str]:
        s = set()
        for d in self.diseases:
            s.update(d.symptom_likelihood.keys())
        return sorted(list(s))
