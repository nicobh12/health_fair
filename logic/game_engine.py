"""game_engine.py - coherent patients with all disease symptoms present."""
import random
from typing import Dict, Any, List, Tuple
from .dataset import Dataset, Disease
from .probability_engine import bayes_with_match

class Patient:
    def __init__(self, true_disease: Disease, force_all_symptoms: bool = True):
        self.true_disease = true_disease
        self.profile = self._generate_profile()
        # If force_all_symptoms: patient has all symptoms where likelihood>0
        if force_all_symptoms:
            self.true_symptoms = [s for s,v in true_disease.symptom_likelihood.items() if v>0]
        else:
            # fallback sampling (not used in v8)
            self.true_symptoms = [s for s,v in true_disease.symptom_likelihood.items() if random.random() < v]
        self.confirmed_symptoms: List[str] = []
        self.negated_symptoms: List[str] = []
        self.symptom_bank: List[str] = []
        self.confidence = round(random.uniform(0.8, 0.98), 2)
        self.family_history_opened = False

    def _generate_profile(self) -> Dict[str, Any]:
        father = random.choice(["Ninguna", "Cáncer de pulmón", "Asma", "Anemia"]).capitalize()
        mother = random.choice(["Ninguna", "Alergia", "Anemia", "Bronquitis"]).capitalize()
        dieta = random.choice(["omnivoro", "vegetariano", "vegano"])
        fuma = random.choice(["sí", "no"])
        return {"padre": father, "madre": mother, "dieta": dieta, "fuma": fuma}

    def prepare_symptom_bank(self, all_symptoms: List[str]):
        self.symptom_bank = [s for s in all_symptoms if s not in self.true_symptoms]

    def answer_question(self, symptom: str) -> Tuple[str, bool]:
        has = symptom in self.true_symptoms
        truthful = random.random() < self.confidence
        if truthful:
            reported = has
        else:
            # occasional lie/misreport
            reported = not has if random.random() < 0.9 else has
        # update observed lists
        if reported and symptom not in self.confirmed_symptoms:
            self.confirmed_symptoms.append(symptom)
            if symptom in self.negated_symptoms:
                self.negated_symptoms.remove(symptom)
        if (not reported) and symptom not in self.negated_symptoms:
            self.negated_symptoms.append(symptom)
            if symptom in self.confirmed_symptoms:
                self.confirmed_symptoms.remove(symptom)
        if symptom in self.symptom_bank:
            self.symptom_bank.remove(symptom)
        return ("sí" if reported else "no"), reported

class GameEngine:
    def __init__(self, dataset: Dataset, force_all_symptoms: bool = True):
        self.dataset = dataset
        self.force_all_symptoms = force_all_symptoms
        self.reset_case()

    def _generate_patient(self) -> Patient:
        priors = self.dataset.priors()
        ids = list(priors.keys())
        chosen = random.choices(ids, weights=[priors[i] for i in ids], k=1)[0]
        true_disease = self.dataset.get_by_id(chosen)
        patient = Patient(true_disease, force_all_symptoms=self.force_all_symptoms)
        patient.prepare_symptom_bank(self.dataset.all_symptoms())
        return patient

    def reset_case(self):
        self.priors = self.dataset.priors()
        self.patient = self._generate_patient()
        self.belief = dict(self.priors)

    def ask_symptom(self, symptom: str) -> Dict[str, Any]:
        ans, reported = self.patient.answer_question(symptom)
        disease_map = {d.id: d.symptom_likelihood for d in self.dataset.diseases}
        # Recalculate posterior using both confirmed and negated symptoms
        self.belief = bayes_with_match(self.belief, self.patient.confirmed_symptoms, self.patient.negated_symptoms, disease_map)
        return {'question': symptom, 'answer': ans, 'reported_bool': reported, 'belief': dict(self.belief)}

    def open_family_history(self) -> Dict[str, str]:
        if not self.patient.family_history_opened:
            self.patient.family_history_opened = True
            for parent in ['padre','madre']:
                val = self.patient.profile.get(parent)
                if val and val != 'Ninguna':
                    for d in self.dataset.diseases:
                        if val.lower() in d.name.lower():
                            self.belief[d.id] *= 1.5
            total = sum(self.belief.values())
            if total > 0:
                for k in self.belief:
                    self.belief[k] /= total
        return self.patient.profile

    def suggest_symptoms(self, n: int = 3) -> List[str]:
        ranked = sorted(self.belief.items(), key=lambda x: -x[1])
        if not ranked:
            return []
        ids = [r[0] for r in ranked]
        candidates = []
        picks = [0, min(len(ids)//2, len(ids)-1), -1]
        for idx in picks:
            d = self.dataset.get_by_id(ids[idx])
            if d.symptom_likelihood:
                top = max(d.symptom_likelihood.items(), key=lambda x: x[1])[0]
                candidates.append(top)
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

    def discard_disease(self, disease_id: str):
        if disease_id in self.belief:
            self.belief[disease_id] = 0.0
            total = sum(self.belief.values())
            if total > 0:
                for k in self.belief:
                    self.belief[k] /= total

    def make_diagnosis(self, disease_id: str) -> bool:
        return disease_id == self.patient.true_disease.id
