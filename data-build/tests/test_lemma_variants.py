# -*- coding: utf-8 -*-
"""The homograph tables behind the claim checker (web/lemma-variants.js).

Run:  python3 -m pytest tests/test_lemma_variants.py
"""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.corpus import load_words, normalize
from pipeline import lemma_variants

_WORDS = load_words()
_VAR = lemma_variants.build(_WORDS)
_FORMS = lemma_variants.form_senses(_WORDS)
_WEB = os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'lemma-variants.js')

def test_angel_king_and_dominion_are_kept_apart():
    senses = {lem: n for lem, n, _root in _VAR['ملك']}
    assert senses['مَلَك'] == 88       # the audited angel count
    assert senses['مُلْك'] == 48
    assert senses['مَلِك'] == 15

def test_senses_add_up_to_the_devoweled_lemma():
    per_norm = Counter(normalize(w['lemma']) for w in _WORDS if w['lemma'])
    for norm, senses in _VAR.items():
        assert len(senses) > 1
        assert sum(n for _lem, n, _root in senses) == per_norm[norm], norm

def test_form_senses_name_the_lemma_behind_each_spelling():
    angel = [v[0] for v in _VAR['ملك']].index('مَلَك')
    assert _FORMS['الملئكة'] == angel                 # only ever angels
    assert dict(_FORMS['الملك']) == {'مُلْك': 19, 'مَلِك': 9}
    assert 'الءاخرة' in _FORMS and 'يوم' not in _FORMS  # يوم has one dictionary lemma
    per_surf = Counter(w['norm'] for w in _WORDS if w['lemma'])
    for surf, x in _FORMS.items():
        if isinstance(x, list):
            assert len(x) > 1 and sum(n for _lem, n in x) == per_surf[surf], surf

def test_web_file_matches_the_corpus():
    expected = ('window.QURAN_LEMMA_VARIANTS = ' + json.dumps(_VAR, ensure_ascii=False, separators=(',', ':'))
                + ';\nwindow.QURAN_FORM_SENSES = ' + json.dumps(_FORMS, ensure_ascii=False, separators=(',', ':')) + ';\n')
    with open(_WEB, encoding='utf-8') as fh:
        assert fh.read() == expected, 'web/lemma-variants.js is stale: run build.py'

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('PASS', name)
