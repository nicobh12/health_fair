"""probability.py - classical probability functions for teaching."""
from typing import Dict, List

def laplace(favorable: int, possible: int) -> float:
    if possible <= 0:
        return 0.0
    return favorable / possible

def conditional(p_a_and_b: float, p_b: float) -> float:
    if p_b == 0:
        return 0.0
    return p_a_and_b / p_b

def total_probability(likelihoods: Dict[str, float], priors: Dict[str, float]) -> float:
    s = 0.0
    for h, p in priors.items():
        s += likelihoods.get(h, 0.0) * p
    return s

def bayes_update(priors: Dict[str, float], likelihoods: Dict[str, float]) -> Dict[str, float]:
    p_e = total_probability(likelihoods, priors)
    post = {}
    if p_e == 0.0:
        s = sum(priors.values())
        if s > 0:
            return {k: v/s for k, v in priors.items()}
        else:
            n = len(priors) or 1
            return {k: 1.0/n for k in priors}
    for h, p in priors.items():
        post[h] = (likelihoods.get(h, 0.0) * p) / p_e
    s = sum(post.values())
    if s > 0:
        return {k: v/s for k, v in post.items()}
    return post
