# -*- coding: utf-8 -*-
"""Monte Carlo + coincidence analysis (MIS775 simulation), honest by design.

Part 1 - Coincidence Lens (descriptive, no fragile inference):
  For each notable number, how many lemmas land exactly on it, and how many fall
  within +/-5. The honest signal: landing on a LARGE number is rare (only ~1
  lemma is within +/-5 of 365), while small numbers like 7 and 12 are crowded
  (thousands nearby). So exact, meaningful matches at large numbers carry the
  real weight; small-number matches are unremarkable. No p-value is claimed,
  because the count distribution is too skewed for a trustworthy null.

Part 2 - Hifz completion-time Monte Carlo (the MIS775 AT3 risk-analysis pattern):
  1,000 trials of a real memorisation schedule with daily output variability and
  missed days, producing the distribution of days-to-finish with P5/P50/P95.
"""
import numpy as np
from collections import Counter

NOTABLE = [7, 12, 19, 24, 30, 40, 50, 60, 70, 77, 88, 99, 100, 114, 313, 354, 360, 365]

def coincidence(words):
    vals = np.array([c for c in Counter(w['lemma'] for w in words if w['lemma']).values()])
    cmax = int(vals.max())
    land = []
    for v in NOTABLE:
        if v > cmax:
            continue
        land.append({'n': v,
                     'exact': int((vals == v).sum()),
                     'near': int(((vals >= v - 5) & (vals <= v + 5)).sum())})
    return {'nLemmas': int(len(vals)), 'landscape': land,
            'note': 'How many of the corpus lemmas land on (or near +/-5) each notable number. '
                    'Large numbers are rare landing spots; small numbers are crowded.'}

def hifz_sim(n_mean=6.667, total=9060, sigma=2.0, miss_prob=0.15, n_trials=1000, seed=7):
    rng = np.random.default_rng(seed)
    days = np.empty(n_trials, dtype=int)
    for t in range(n_trials):
        done = 0.0
        d = 0
        while done < total and d < 50000:
            d += 1
            if rng.random() < miss_prob:
                continue                       # a missed day
            done += max(0.0, rng.normal(n_mean, sigma))
        days[t] = d
    p5, p50, p95 = np.percentile(days, [5, 50, 95])
    # histogram for the UI
    lo, hi = int(days.min()), int(days.max())
    bins = np.linspace(lo, hi, 21)
    counts, edges = np.histogram(days, bins=bins)
    return {
        'params': {'newLinesPerDayMean': n_mean, 'sigma': sigma, 'missProb': miss_prob,
                   'totalLines': total, 'trials': n_trials},
        'meanDays': round(float(days.mean()), 0),
        'p5': int(p5), 'p50': int(p50), 'p95': int(p95),
        'meanYears': round(float(days.mean()) / 365.0, 1),
        'p95Years': round(float(p95) / 365.0, 1),
        'hist': [{'day': int((edges[i] + edges[i + 1]) / 2), 'count': int(counts[i])}
                 for i in range(len(counts))],
        'note': '1,000-trial simulation with daily variability and a 15% missed-day rate; '
                'the deterministic LP gives the mean, the simulation gives the risk band.',
    }

def build(words):
    return {'coincidence': coincidence(words), 'hifzSim': hifz_sim()}

if __name__ == '__main__':
    import json
    from .corpus import load_words
    print(json.dumps(build(load_words()), indent=2, ensure_ascii=False))
