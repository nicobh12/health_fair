"""dataset.py - carga el banco de enfermedades y el mapa de síntomas."""
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
        return float(self.symptom_likelihood.get(symptom, 0.0))

class Dataset:
    def __init__(self, path: str, symptom_map_path: str):
        self.path = Path(path)
        self.symptom_map_path = Path(symptom_map_path)
        self.diseases = self._load()
        self.symptom_map = self._load_symptom_map()

    def _load(self) -> List[Disease]:
        with open(self.path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        return [Disease(d) for d in raw.get('diseases', [])]

    def _load_symptom_map(self) -> Dict[str, str]:
        with open(self.symptom_map_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def priors(self) -> Dict[str, float]:
        raw = {d.id: float(d.prior) for d in self.diseases}
        total = sum(raw.values())
        if total <= 0:
            n = len(raw) or 1
            return {k: 1.0/n for k in raw}
        return {k: v/total for k, v in raw.items()}

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

    def display_to_key(self) -> Dict[str, str]:
        return self.symptom_map
