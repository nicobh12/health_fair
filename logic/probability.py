
"""probability.py
Implements Bayes updates, probability total and helpers for combining evidence.
"""
from typing import Dict, Iterable
import math

def normalize(dist: Dict[str, float]) -> Dict[str, float]:
    total = sum(dist.values())
    if total <= 0:
        # avoid division by zero; return uniform
        n = len(dist)
        return {k: 1.0/n for k in dist}
    return {k: v/total for k, v in dist.items()}

def bayes_update(priors: Dict[str, float], likelihoods: Dict[str, float]) -> Dict[str, float]:
    """Perform a Bayes update given priors P(H) and likelihoods P(E|H).
    Returns posterior P(H|E) proportional to P(E|H) * P(H).
    """
    posterior_raw = {}
    for h, p in priors.items():
        lam = likelihoods.get(h, 0.01)
        posterior_raw[h] = p * lam
    return normalize(posterior_raw)

def probability_total(priors: Dict[str, float], evidence_models: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """Compute P(E) for each evidence when evidence could come from multiple hypotheses.
    evidence_models maps evidence -> {hypothesis: P(E|H)}
    Returns mapping evidence -> P(E).
    """
    results = {}
    for e, model in evidence_models.items():
        s = 0.0
        for h, p_h in priors.items():
            s += p_h * model.get(h, 0.0)
        results[e] = s
    return results

def combine_independent_likelihoods(disease_likelihoods: Iterable[Dict[str, float]]) -> Dict[str, float]:
    """If multiple symptoms assumed independent given disease, combine by multiplying likelihoods.
    Each dict maps hypothesis -> P(symptom_i | hypothesis)
    Returns combined P(all symptoms | hypothesis)
    """
    combined = {}
    for like in disease_likelihoods:
        for h, val in like.items():
            combined[h] = combined.get(h, 1.0) * val
    return combined
