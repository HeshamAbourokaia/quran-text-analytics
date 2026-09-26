# -*- coding: utf-8 -*-
"""Lemmas that share one spelling once the vowel marks are removed.

The web word index stores de-voweled lemmas, so homographs merge there: angel
(malak), dominion (mulk) and king (malik) are all "ملك". This table keeps them
apart for the frontend: for every de-voweled lemma that covers more than one
dictionary lemma, the voweled lemmas with their word counts and roots, most
frequent first. The claims engine uses the same rule (most frequent lemma wins),
so counts in the browser match the audited figures.
"""
from collections import Counter, defaultdict
from .corpus import normalize


def build(words):
    by_norm = defaultdict(Counter)
    roots = {}
    for w in words:
        if not w['lemma']:
            continue
        by_norm[normalize(w['lemma'])][w['lemma']] += 1
        roots.setdefault(w['lemma'], normalize(w['root']) if w['root'] else '')
    return {
        norm: [[lem, n, roots[lem]] for lem, n in counts.most_common()]
        for norm, counts in sorted(by_norm.items())
        if len(counts) > 1
    }



def form_senses(words):
    """Which dictionary lemma a written form stands for, where the de-voweled index can't tell.

    A plain text search counts every word written the same way, so "ملك" finds angel, king and
    dominion together, while "الملئكة" is only ever angels. For each written form of a lemma whose
    spelling covers several dictionary words (see build), this gives the index of its lemma in that
    entry of build(). A form that stands for several lemmas gets each lemma with its count instead.
    Forms of unambiguous lemmas are left out: the word index already knows them.
    """
    variants = build(words)
    by_surf = defaultdict(Counter)
    for w in words:
        if w['lemma']:
            by_surf[w['norm']][w['lemma']] += 1
    out = {}
    for surf, counts in sorted(by_surf.items()):
        if len(counts) > 1:
            out[surf] = [[lem, n] for lem, n in counts.most_common()]
            continue
        (lem, _n), = counts.items()
        senses = variants.get(normalize(lem))
        if senses:
            out[surf] = [v[0] for v in senses].index(lem)
    return out
