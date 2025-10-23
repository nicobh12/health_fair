"""game_engine.py - classical Bayes update game engine"""
import random
from typing import Dict, Any, List, Tuple
from .dataset import Dataset, Disease
from .probability import bayes_update

# fixed conditional probabilities for teaching
P_IF_HAS = 0.8
P_IF_NOT = 0.2

class Patient:
    def __init__(self, true_disease: Disease):
        self.true_disease = true_disease
        self.profile = self._generate_profile()
        # sample symptoms using frequentist Bernoulli with p = 0.8 if disease has symptom else 0.2
        self.true_symptoms = self._sample_symptoms()
        self.confirmed: List[str] = []
        self.negated: List[str] = []
        self.symptom_bank: List[str] = []

    def _generate_profile(self) -> Dict[str, Any]:
        return {"padre":"Ninguna","madre":"Ninguna","dieta":"omnivoro","fuma":"no"}

    def _sample_symptoms(self) -> List[str]:
        chosen = []
        for s in self.true_disease.symptoms:
            if random.random() < P_IF_HAS:
                chosen.append(s)
        return chosen

    def prepare_symptom_bank(self, all_symptoms: List[str]):
        self.symptom_bank = [s for s in all_symptoms if s not in self.true_symptoms]

    def answer(self, symptom: str) -> Tuple[str, bool]:
        has = symptom in self.true_symptoms
        # assume truthful reporting for clarity
        reported = has
        if reported and symptom not in self.confirmed:
            self.confirmed.append(symptom)
            if symptom in self.negated:
                self.negated.remove(symptom)
        if (not reported) and symptom not in self.negated:
            self.negated.append(symptom)
            if symptom in self.confirmed:
                self.confirmed.remove(symptom)
        if symptom in self.symptom_bank:
            self.symptom_bank.remove(symptom)
        return ("sí" if reported else "no"), reported

class GameEngine:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.reset_case()

    def _generate_patient(self) -> Patient:
        priors = self.dataset.priors()
        ids = list(priors.keys())
        chosen = random.choices(ids, weights=[priors[i] for i in ids], k=1)[0]
        true_disease = self.dataset.get_by_id(chosen)
        p = Patient(true_disease)
        p.prepare_symptom_bank(self.dataset.all_symptoms())
        return p

    def reset_case(self):
        self.priors = self.dataset.priors()
        self.patient = self._generate_patient()
        self.belief = dict(self.priors)

    def _likelihoods_for_symptom(self, symptom: str, positive: bool) -> Dict[str, float]:
        likes = {}
        for d in self.dataset.diseases:
            if symptom in d.symptoms:
                p = P_IF_HAS
            else:
                p = P_IF_NOT
            likes[d.id] = p if positive else (1.0 - p)
        return likes

    def recalc_belief(self):
        # compute combined likelihood for each disease
        likes = {d.id: 1.0 for d in self.dataset.diseases}
        for s in self.patient.confirmed:
            l = self._likelihoods_for_symptom(s, positive=True)
            for h in likes:
                likes[h] *= l.get(h, 0.0)
        for s in self.patient.negated:
            l = self._likelihoods_for_symptom(s, positive=False)
            for h in likes:
                likes[h] *= l.get(h, 0.0)
        # apply Bayes
        self.belief = bayes_update(self.priors, likes)

    def ask_symptom(self, symptom: str) -> Dict[str, Any]:
        ans, reported = self.patient.answer(symptom)
        self.recalc_belief()
        return {'question': symptom, 'answer': ans, 'reported_bool': reported, 'belief': dict(self.belief)}

    def suggest_symptoms(self, n: int = 3) -> List[str]:
        ranked = sorted(self.belief.items(), key=lambda x: -x[1])
        if not ranked:
            return []
        ids = [r[0] for r in ranked]
        candidates = []
        picks = [0, min(len(ids)//2, len(ids)-1), -1]
        for idx in picks:
            d = self.dataset.get_by_id(ids[idx])
            if d.symptoms:
                candidates.append(d.symptoms[0])
        unique = []
        for s in candidates:
            if s in self.patient.symptom_bank and s not in unique:
                unique.append(s)
        all_s = self.dataset.all_symptoms()
        random.shuffle(all_s)
        for s in all_s:
            if len(unique) >= n:
                break
            if s in self.patient.symptom_bank and s not in unique:
                unique.append(s)
        return unique[:n]

    def open_family_history(self):
        return self.patient.profile

    def discard_disease(self, disease_id: str):
        if disease_id in self.belief:
            self.belief[disease_id] = 0.0
            total = sum(self.belief.values())
            if total > 0:
                for k in self.belief:
                    self.belief[k] /= total

    def make_diagnosis(self, disease_id: str) -> bool:
        return disease_id == self.patient.true_disease.id
