import random, csv

class DiagnosisEngine:
    def __init__(self, diseases_path, symptoms_path):
        self.diseases = self.load_diseases(diseases_path)
        self.symptoms = self.load_symptoms(symptoms_path)
        self.all_symptoms = sorted(set(s for d in self.diseases.values() for s in d['sintomas']))
        self.real_disease = random.choice(list(self.diseases.keys()))
        self.known = set()
        self.probs = {k: v['prior'] for k, v in self.diseases.items()}
        self.normalize()
    def load_diseases(self, path):
        diseases = {}
        with open(path, encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                code = row['codigo']
                sintomas = [s.strip() for s in row['sintomas'].split(',')]
                diseases[code] = {'nombre': row['nombre'], 'sintomas': sintomas, 'prior': float(row['prior'])}
        return diseases
    def load_symptoms(self, path):
        with open(path, encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    def normalize(self):
        s = sum(self.probs.values())
        for k in self.probs:
            self.probs[k] /= s
    def get_probabilities(self): return dict(sorted(self.probs.items(), key=lambda x: -x[1]))
    def choose_symptom(self):
        remaining = [s for s in self.all_symptoms if s not in self.known]
        return random.choice(remaining) if remaining else None
    def patient_has(self, symptom):
        self.known.add(symptom)
        return symptom in self.diseases[self.real_disease]['sintomas']
    def update_probabilities(self, symptom, has):
        for code, info in self.diseases.items():
            p_symptom_given_disease = 1 if symptom in info['sintomas'] else 0.1
            if has:
                self.probs[code] *= p_symptom_given_disease
            else:
                self.probs[code] *= (1 - p_symptom_given_disease)
        self.normalize()
    def diagnose(self):
        print("\nEnfermedades no descartadas:")
        for code in self.diseases:
            print(f" ({code}) {self.diseases[code]['nombre']}")
        guess = input("\nCódigo: ").strip().upper()
        if guess == self.real_disease:
            print("\n✅ Diagnóstico correcto!")
        else:
            print(f"\n❌ Incorrecto. La enfermedad real era: {self.diseases[self.real_disease]['nombre']}")
        input("Presiona Enter para salir...")
