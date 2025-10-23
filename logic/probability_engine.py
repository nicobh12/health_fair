"""probability_engine.py
Módulo con todos los cálculos probabilísticos. Cada función incluye un comentario
indicando qué concepto estadístico implementa.
"""
from typing import Dict, List

# -----------------------------
# Conceptos básicos / Teorema de Laplace
# -----------------------------
def laplace_probability(favorable: int, possible: int) -> float:
    """P(A) = casos favorables / casos posibles (Teorema de Laplace)"""
    if possible <= 0:
        return 0.0
    return favorable / possible

# -----------------------------
# Probabilidad condicionada
# -----------------------------
def conditional(p_a_and_b: float, p_b: float) -> float:
    """P(A|B) = P(A ∧ B) / P(B) (Probabilidad condicionada)"""
    if p_b == 0:
        return 0.0
    return p_a_and_b / p_b

# -----------------------------
# Probabilidad total
# -----------------------------
def total_probability(p_b_given_a: Dict[str, float], p_a: Dict[str, float]) -> float:
    """P(B) = Σ P(B|A_i) P(A_i) (Probabilidad total)"""
    s = 0.0
    for a, pa in p_a.items():
        s += p_b_given_a.get(a, 0.0) * pa
    return s

# -----------------------------
# Teorema de Bayes
# -----------------------------
def bayes_update(priors: Dict[str, float], likelihoods: Dict[str, float]) -> Dict[str, float]:
    """Aplica Bayes: P(A_i|B) = P(B|A_i)*P(A_i) / P(B)"""
    # P(B)
    p_b = total_probability(likelihoods, priors)
    post = {}
    for h, p in priors.items():
        post[h] = (likelihoods.get(h, 0.0) * p) / p_b if p_b > 0 else 0.0
    # Normalizar por si hay errores numéricos
    total = sum(post.values())
    if total > 0:
        for k in post:
            post[k] = post[k] / total
    return post

# -----------------------------
# Enfoque frecuentista
# -----------------------------
def frequentist(successes: int, trials: int) -> float:
    """Estimación por frecuencia relativa: P(A) ≈ n(A)/N"""
    if trials <= 0:
        return 0.0
    return successes / trials

# -----------------------------
# Función de actualización que usa lo anterior
# -----------------------------
def update_with_symptom(priors: Dict[str, float],
                        symptom: str,
                        has_symptom: bool,
                        disease_symptom_map: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """Recalcula las probabilidades de todas las enfermedades dado un nuevo síntoma.

    Implementa:
    - Probabilidad condicionada a través de modelar P(symptom|disease)
    - Probabilidad total para normalizar y calcular P(symptom)
    - Teorema de Bayes para obtener las posteriors
    """
    # Construimos P(E | H) para cada hipótesis H (enfermedad)
    p_e_given_h = {}
    for h in priors:
        p = disease_symptom_map.get(h, {}).get(symptom, 0.01)
        # si el paciente NO tiene el síntoma, usamos 1 - P(symptom|h)
        p_e_given_h[h] = p if has_symptom else (1 - p)

    # Aplicamos Bayes usando la función bayes_update (que internamente usa probabilidad total)
    new_post = bayes_update(priors, p_e_given_h)

    return new_post
