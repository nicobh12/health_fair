"""probability_engine.py
Robust Bayes + match_ratio weighting + additive blending to avoid underflow.
"""
from typing import Dict, List
import math

EPS = 1e-12
MIN_LIKE = 1e-4

# Critical symptoms per disease
CRITICAL = {
    'CC': ['sangre_tos', 'perdida_peso'],
    'NE': ['fiebre', 'falta_aire'],
    'CO': ['perdida_gusto', 'fiebre']
}

def safe_log(x: float) -> float:
    return math.log(max(x, EPS))

def logsumexp(vals: List[float]) -> float:
    m = max(vals)
    s = sum(math.exp(v - m) for v in vals)
    return m + math.log(s)

def bayes_with_match(priors: Dict[str, float],
                     confirmed: List[str],
                     negated: List[str],
                     symptom_map: Dict[str, Dict[str, float]],
                     alpha: float = 5.0,
                     smoother: float = 0.08,
                     min_floor: float = 1e-10) -> Dict[str, float]:
    ids = list(priors.keys())
    # match ratio: confirmed symptoms matching disease / total disease symptoms
    match_ratio = {}
    for h in ids:
        total_syms = max(len(symptom_map.get(h, {})), 1)
        matches = sum(1 for s in confirmed if s in symptom_map.get(h, {}))
        match_ratio[h] = matches / total_syms

    # log-bayes part
    log_prior = {h: safe_log(priors.get(h, 0.0)) for h in ids}
    log_like = {h: 0.0 for h in ids}
    for s in confirmed:
        for h in ids:
            p = symptom_map.get(h, {}).get(s, MIN_LIKE)
            p = max(p, MIN_LIKE)
            log_like[h] += safe_log(p)
    for s in negated:
        for h in ids:
            p = symptom_map.get(h, {}).get(s, MIN_LIKE)
            p = min(max(p, MIN_LIKE), 1 - 1e-9)
            log_like[h] += safe_log(1.0 - p)

    log_post_raw = [log_prior[h] + log_like[h] for h in ids]
    lse = logsumexp(log_post_raw)
    bayes_post = {h: math.exp((log_prior[h] + log_like[h]) - lse) for h in ids}

    # additive blending: factor = 1 + alpha*match_ratio + smoother
    blended = {}
    for h in ids:
        factor = 1.0 + alpha * match_ratio.get(h, 0.0) + smoother
        blended_val = bayes_post.get(h, 0.0) * factor
        blended[h] = max(blended_val, min_floor)

    # critical symptom penalty
    for h in ids:
        crits = CRITICAL.get(h, [])
        if crits:
            any_confirmed = any(c in confirmed for c in crits)
            if not any_confirmed:
                blended[h] *= 0.2

    total = sum(blended.values())
    if total <= 0 or any(math.isnan(v) for v in blended.values()):
        s = sum(priors.values())
        if s > 0:
            return {k: v/s for k, v in priors.items()}
        else:
            n = len(priors) or 1
            return {k: 1.0/n for k in priors}
    return {k: v/total for k, v in blended.items()}
