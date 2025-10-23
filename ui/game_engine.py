"""game_engine.py
Motor del juego: genera pacientes, mantiene listas de síntomas, llama al probability_engine
"""
import random
from typing import Dict, Any, List, Tuple
from .dataset import Dataset, Disease
from .probability_engine import update_with_symptom

class Patient:
    def __init__(self, true_disease: Disease):
        self.true_disease = true_disease
        self.profile = self._generate_profile()
        # sintomas que el paciente efectivamente tiene (usado para respuestas verdaderas)
        self.true_symptoms = self._sample_true_symptoms()
        # symptoms confirmed by asking (observed yes)
        self.confirmed_symptoms: List[str] = []
        # symptom bank available to ask (initially all symptoms)
        self.symptom_bank: List[str] = []
        self.confidence = round(random.uniform(0.6, 0.95), 2)

    def _generate_profile(self) -> Dict[str, Any]:
        father = random.choice(["Ninguna", "Cáncer de pulmón", "Asma", "Anemia"])
        mother = random.choice(["Ninguna", "Alergia", "Anemia", "Bronquitis"])
        dieta = random.choice(["omnivoro", "vegetariano", "vegano"])
        fuma = random.choice(["sí", "no"])
        return {"padre": father, "madre": mother, "dieta": dieta, "fuma": fuma}

    def _sample_true_symptoms(self) -> List[str]:
        # sample symptoms from the disease likelihoods (stochastic)
        items = list(self.true_disease.symptom_likelihood.items())
        names = [k for k, _ in items]
        weights = [v for _, v in items]
        if not names:
            return []
        total = sum(weights)
        probs = [w/total for w in weights] if total > 0 else [1/len(names)]*len(names)
        k = 1 if random.random() < 0.7 else random.randint(1, min(3, len(names)))
        chosen = random.choices(names, probs, k=k)
        return list(set(chosen))

    def prepare_symptom_bank(self, all_symptoms: List[str]):
        # bank starts as all symptoms minus those already in true_symptoms
        self.symptom_bank = [s for s in all_symptoms if s not in self.true_symptoms]

    def answer_question(self, symptom: str) -> Tuple[str, bool]:
        """Return ('sí'/'no', reported_bool). Report may be noisy depending on confidence."""
        # determine ground truth
        has = symptom in self.true_symptoms
        # truthfulness sampling
        truthful = random.random() < self.confidence
        if truthful:
            reported = has
        else:
            # lies occasionally, or mistakes
            reported = not has if random.random() < 0.9 else has
        # if reported yes and it's new, add to confirmed symptoms
        if reported and symptom not in self.confirmed_symptoms:
            self.confirmed_symptoms.append(symptom)
        # remove symptom from bank so it cannot be asked again
        if symptom in self.symptom_bank:
            self.symptom_bank.remove(symptom)
        return ("sí" if reported else "no"), reported

class GameEngine:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.reset_case()

    def reset_case(self):
        self.priors = self.dataset.priors()
        self.patient = self._generate_patient()
        # initialize belief distribution as priors
        self.belief = dict(self.priors)
        # prepare symptom bank for the patient
        all_symptoms = self.dataset.all_symptoms()
        self.patient.prepare_symptom_bank(all_symptoms)

    def _generate_patient(self) -> Patient:
        ids = list(self.priors.keys())
        probs = [self.priors[i] for i in ids]
        true_id = random.choices(ids, probs, k=1)[0]
        true_disease = self.dataset.get_by_id(true_id)
        return Patient(true_disease)

    def ask_symptom(self, symptom: str) -> Dict[str, Any]:
        # patient answers
        ans, reported = self.patient.answer_question(symptom)
        # recompute probabilities for ALL diseases after this observation
        # Here: probability_engine.update_with_symptom implements Bayes + prob. total + condicionada
        disease_map = {d.id: d.symptom_likelihood for d in self.dataset.diseases}
        self.belief = update_with_symptom(self.belief, symptom, bool(reported), disease_map)
        return {'question': symptom, 'answer': ans, 'reported_bool': reported, 'belief': dict(self.belief)}

    def suggest_symptoms(self, n: int = 3) -> List[str]:
        """Return up to n symptoms: one likely, one medium, one unlikely (based on current belief)."""
        ranked = sorted(self.belief.items(), key=lambda x: -x[1])
        if not ranked:
            return []
        ids = [r[0] for r in ranked]
        likely = self.dataset.get_by_id(ids[0])
        mid = self.dataset.get_by_id(ids[min(len(ids)//2, len(ids)-1)])
        unlikely = self.dataset.get_by_id(ids[-1])
        # choose top symptom from each disease
        options = []
        for d in [likely, mid, unlikely]:
            if d.symptom_likelihood:
                top = max(d.symptom_likelihood.items(), key=lambda x: x[1])[0]
                options.append(top)
        # ensure options are available in symptom_bank; if not, add other symptoms
        available = [s for s in options if s in self.patient.symptom_bank]
        # fill with random symptoms if needed
        all_symptoms = self.dataset.all_symptoms()
        random.shuffle(all_symptoms)
        for s in all_symptoms:
            if len(available) >= n:
                break
            if s not in available and s in self.patient.symptom_bank:
                available.append(s)
        return available[:n]

    def discard_disease(self, disease_id: str):
        if disease_id in self.belief:
            self.belief[disease_id] = 0.0
            total = sum(self.belief.values())
            if total > 0:
                for k in self.belief:
                    self.belief[k] /= total

    def make_diagnosis(self, disease_id: str) -> bool:
        return disease_id == self.patient.true_disease.id
