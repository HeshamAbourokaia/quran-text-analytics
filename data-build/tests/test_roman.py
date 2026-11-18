# -*- coding: utf-8 -*-
"""Pin how dictionary words are sounded out, and that the site's file carries the same table.

Run:  python3 tests/test_roman.py      (or: pytest)
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.corpus import load_words, normalize
from pipeline.roman import build, sound

_WORDS = load_words()
_R = build(_WORDS)
_WEB = os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'roman.js')

def test_every_word_has_a_sound():
    bare = {normalize(w['lemma']) for w in _WORDS if w['lemma']}
    assert {b for b in bare if len(b) > 1} == set(_R)
    ok = set("abdfghijklmnqrstuwxyzAIUEHSDTZvp*$' ")
    assert all(set(v) <= ok and v.strip() == v for v in _R.values())

def test_short_and_long_vowels():
    assert _R['رحمة'] == 'raHmap' and _R['كتاب'] == 'kitAb' and _R['رسول'] == 'rasUl' and _R['رحيم'] == 'raHIm'
    assert _R['ايمان'] == "'ImAn" and _R['قرءان'] == "qur'An" and _R['نور'] == 'nUr' and _R['نار'] == 'nAr'

def test_glides_and_weak_endings():
    assert _R['يوم'] == 'yawm' and _R['خير'].split()[0] == 'xayr' and _R['شيطان'] == '$ayTAn' and _R['فرعون'] == 'firEawn'
    assert _R['موسي'] == 'mUsA' and _R['عيسي'] == 'EIsA' and _R['قيامة'] == 'qiyAmap' and _R['حياة'] == 'HayAp'
    assert _R['نبي'] == 'nabI' and 'EadU' in _R['عدو'].split() and 'hudA' in _R['هدي'].split()

def test_doubled_letters_and_the_article():
    assert _R['جنة'].split()[0] == 'jannap' and _R['جهنم'] == 'jahannam' and _R['محمد'] == 'muHammad'
    assert _R['الله'] == 'allAh' and _R['الذي'] == 'alla*I'

def test_an_alif_that_only_carries_a_vowel():
    assert _R['اسم'] == 'ism' and _R['ابن'].split()[0] == 'ibn' and _R['استغفر'] == 'istagfara'
    assert sound('الْيَسَع', 'N') == 'alyasaE'

def test_one_spelling_several_words():
    assert _R['ملك'] == 'malak mulk malik malk'               # angel, dominion, king: most frequent first
    assert _R['علم'].split()[:2] == ['Ealima', 'Eilm']

def test_the_site_carries_the_same_table():
    s = open(_WEB, encoding='utf-8').read()
    assert json.loads(s[s.index('{'):s.rindex('}') + 1]) == _R

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
