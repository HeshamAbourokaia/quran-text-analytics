// Jev features, browser side (also loaded by the Node tests in data-build/jev).
//
// Every feature works with plain matching over the corpus. When web/config.js names a Jev endpoint
// (the /api/decide function), a few judgement calls are also asked of TypeSafe's Jev: which word a
// claim is about and how it counts, which page a question belongs on, which kind of du'a or lesson
// fits a situation. Numbers always come from the corpus. Nothing is sent anywhere unless
// jevEndpoint is set.
(function (root) {
  'use strict';

  // Same rules as normalize() in app.html and data-build/pipeline/corpus.py.
  const TASHKEEL = /[ؐ-ًؚ-ٰٟۖ-ۭٓ-ٕ]/g;
  function normalize(s) {
    if (!s) return '';
    return String(s).replace(/﻿/g, '').replace(TASHKEEL, '')
      .replace(/[ٱآأإ]/g, 'ا').replace(/ى/g, 'ي').trim();
  }
  // Voweled lemmas are compared in canonical (NFC) order, so the order of stacked marks doesn't matter.
  const canon = s => String(s || '').normalize('NFC');
  const latinDigits = s => String(s)
    .replace(/[٠-٩]/g, d => d.charCodeAt(0) - 0x0660)
    .replace(/[۰-۹]/g, d => d.charCodeAt(0) - 0x06F0);

  // ---- the call to /api/decide ----

  function endpoint() {
    const c = root.QTA_CONFIG;
    return c && typeof c.jevEndpoint === 'string' ? c.jevEndpoint.trim() : '';
  }

  // null when Jev is not configured, { ok:false } when the call failed, else the endpoint's answer.
  async function decide(payload, { timeoutMs = 9000, fetchImpl } = {}) {
    const url = endpoint();
    if (!url) return null;
    const doFetch = fetchImpl || root.fetch;
    const ctrl = typeof AbortController === 'function' ? new AbortController() : null;
    const timer = ctrl ? setTimeout(() => ctrl.abort(), timeoutMs) : null;
    try {
      const r = await doFetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload), signal: ctrl ? ctrl.signal : undefined });
      const j = await r.json().catch(() => null);
      return r.ok && j && j.ok ? j : { ok: false, status: r.status, error: j && j.error };
    } catch (e) {
      return { ok: false, error: e && e.name === 'AbortError' ? 'timeout' : 'network' };
    } finally {
      if (timer) clearTimeout(timer);
    }
  }

  // Jev's answer replaces what plain matching found only when the two agree, when plain matching
  // found nothing, or when Jev is reasonably sure. Otherwise Jev's pick is offered as an alternative.
  const SURE = 0.5;
  function trust(answer, local) {
    if (!answer || answer.value == null) return false;
    if (local == null || answer.value === local) return true;
    return answer.confidence == null || answer.confidence >= SURE;
  }

  // ---- the word index ----

  // Built once from window.QURAN_WORDS (parallel arrays), QURAN_LEMMA_VARIANTS and QURAN_FORM_SENSES.
  function makeIndex(W, VAR, FS) {
    const lemmaCount = new Map(), lemmaRoot = new Map(), rootCount = new Map();
    const surfCount = new Map(), surfLemmas = new Map(), lemmaSurfs = new Map();
    for (let i = 0; i < W.norm.length; i++) {
      const s = W.norm[i], l = W.lemma[i], r = W.root[i];
      surfCount.set(s, (surfCount.get(s) || 0) + 1);
      if (l) {
        lemmaCount.set(l, (lemmaCount.get(l) || 0) + 1);
        if (r && !lemmaRoot.has(l)) lemmaRoot.set(l, r);
        let m = surfLemmas.get(s);
        if (!m) surfLemmas.set(s, (m = new Map()));
        m.set(l, (m.get(l) || 0) + 1);
        let f = lemmaSurfs.get(l);
        if (!f) lemmaSurfs.set(l, (f = new Map()));
        f.set(s, (f.get(s) || 0) + 1);
      }
      if (r) rootCount.set(r, (rootCount.get(r) || 0) + 1);
    }
    // The mushaf often spells a word differently from modern Arabic (الملئكة for الملائكة, الحيوة for الحياة).
    // Forms compared without alifs and hamzas find each other.
    const skel = new Map();
    for (const [surf, n] of surfCount) {
      const k = skeleton(surf);
      let m = skel.get(k);
      if (!m) skel.set(k, (m = new Map()));
      m.set(surf, n);
    }
    return { W, VAR: VAR || {}, FS: FS || {}, lemmaCount, lemmaRoot, rootCount, surfCount, surfLemmas, lemmaSurfs, skel, cite: new Map() };
  }
  function skeleton(w) {
    return w.replace(/[اء]/g, '').replace(/وة/g, 'ة').replace(/ة/g, 'ه');
  }

  // Clitics that can sit in front of a word in the Uthmani text (conjunction, preposition, article).
  const PREFIXES = ['', 'و', 'ف', 'ب', 'ل', 'ك', 'ال', 'وال', 'فال',
    'بال', 'كال', 'لل', 'ولل', 'فلل', 'وب', 'فب',
    'ول', 'فل', 'وك', 'فك', 'وبال', 'فبال', 'وكال'];

  // Words written exactly as `form`, with or without a leading conjunction, preposition or article.
  function formCount(ix, form) {
    if (!form) return 0;
    let n = 0;
    for (const p of PREFIXES) n += ix.surfCount.get(p + form) || 0;
    return n;
  }

  // How the mushaf writes a lemma's dictionary form (شيطان is written شيطن, حياة is written حيوة): the
  // commonest of the lemma's written forms that, once a leading clitic is removed, is the same word
  // apart from alifs and hamzas. null when the dictionary form never occurs as written (عقل only
  // occurs as a verb).
  function citationForm(ix, norm) {
    if (ix.cite.has(norm)) return ix.cite.get(norm);
    let best = null;
    if (ix.surfCount.has(norm)) best = norm;
    else {
      const want = skeleton(norm), found = new Map();
      for (const [surf, n] of ix.lemmaSurfs.get(norm) || []) {
        for (const p of PREFIXES) {
          if (!surf.startsWith(p)) continue;
          const x = surf.slice(p.length);
          if (x.length >= 2 && skeleton(x) === want) found.set(x, (found.get(x) || 0) + n);
        }
      }
      if (found.size) best = byCount(found)[0];
    }
    ix.cite.set(norm, best);
    return best;
  }

  // The dictionary lemmas (voweled) behind one written form, with counts, when the de-voweled index
  // can't tell them apart; null when the form's lemma is unambiguous.
  function formSenses(ix, surf) {
    const x = ix.FS[surf];
    if (x == null) return null;
    if (Array.isArray(x)) return x;
    const [norm, n] = [...(ix.surfLemmas.get(surf) || [])][0] || [];
    const v = norm && ix.VAR[norm] && ix.VAR[norm][x];
    return v ? [[v[0], n]] : null;
  }

  // Of the words written exactly as `form` (with any leading clitic), how many are a different
  // dictionary word from `opt`: the angel count "as written" also finds king and dominion.
  function formOthers(ix, form, opt) {
    if (!form) return 0;
    const mine = l => (opt.sense ? canon(l) === canon(opt.sense) : normalize(l) === opt.norm);
    let n = 0;
    for (const p of PREFIXES) {
      const surf = p + form;
      if (!ix.surfCount.has(surf)) continue;
      const senses = formSenses(ix, surf);
      if (senses) { for (const [l, c] of senses) if (!mine(l)) n += c; }
      else for (const [l, c] of ix.surfLemmas.get(surf) || []) if (l !== opt.norm) n += c;
    }
    return n;
  }

  // How the search box would count a query in each mode (same rules as runSearch in app.html).
  function modeCounts(ix, q) {
    q = normalize(q);
    if (!q) return { surface: 0, lemma: 0, root: 0 };
    let surface = 0;
    for (const [s, n] of ix.surfCount) if (s.includes(q)) surface += n;
    return { surface, lemma: ix.lemmaCount.get(q) || 0, root: ix.rootCount.get(q) || 0 };
  }

  // ---- English words people use in claims, mapped to the corpus ----
  // norm: the de-voweled lemma in the word index. sense: the voweled lemma, when the spelling covers
  // several dictionary words (see lemma-variants.js). Several options = genuinely ambiguous English.
  const o = (norm, sense, form) => Object.assign({ norm }, sense ? { sense } : null, form ? { form } : null);
  const GLOSS = {
    'day': [o('يوم')], 'days': [o('يوم')], 'month': [o('شهر')], 'year': [o('سنة', 'سَنَة'), o('عام')],
    'angel': [o('ملك', 'مَلَك')], 'king': [o('ملك', 'مَلِك')], 'dominion': [o('ملك', 'مُلْك')], 'kingdom': [o('ملك', 'مُلْك')], 'sovereignty': [o('ملك', 'مُلْك')],
    'devil': [o('شيطان')], 'satan': [o('شيطان')], 'shaytan': [o('شيطان')], 'iblis': [o('ابليس')],
    'hell': [o('جهنم')], 'jahannam': [o('جهنم')], 'fire': [o('نار')],
    'paradise': [o('جنة', 'جَنَّة')], 'jannah': [o('جنة', 'جَنَّة')], 'garden': [o('جنة', 'جَنَّة')],
    'heaven': [o('جنة', 'جَنَّة'), o('سماء')], 'sky': [o('سماء')], 'earth': [o('ارض')],
    'jinn': [o('جن', 'جِنّ')], 'man': [o('رجل', 'رَجُل')], 'men': [o('رجل', 'رَجُل')], 'woman': [o('امرات')], 'women': [o('نساء')],
    'human': [o('انسان'), o('بشر', 'بَشَر')], 'people': [o('ناس')], 'mankind': [o('ناس')],
    'jesus': [o('عيسي')], 'isa': [o('عيسي')], 'adam': [o('ادم')], 'moses': [o('موسي')], 'musa': [o('موسي')],
    'abraham': [o('ابراهيم')], 'ibrahim': [o('ابراهيم')], 'noah': [o('نوح')], 'nuh': [o('نوح')], 'joseph': [o('يوسف')], 'yusuf': [o('يوسف')],
    'mary': [o('مريم')], 'maryam': [o('مريم')], 'pharaoh': [o('فرعون')], 'muhammad': [o('محمد')],
    'allah': [o('الله')], 'god': [o('الله')], 'lord': [o('رب', 'رَبّ')], 'rabb': [o('رب', 'رَبّ')],
    'world': [o('دنيا')], 'dunya': [o('دنيا')], 'hereafter': [o('اخر', 'آخِر', 'ءاخرة')], 'akhirah': [o('اخر', 'آخِر', 'ءاخرة')], 'akhira': [o('اخر', 'آخِر', 'ءاخرة')],
    'life': [o('حياة')], 'death': [o('موت')], 'dead': [o('ميت', 'مَيِّت')],
    'sea': [o('بحر')], 'land': [o('بر', 'بَرّ')], 'righteousness': [o('بر', 'بِرّ')],
    'sun': [o('شمس')], 'moon': [o('قمر')], 'star': [o('نجم')], 'night': [o('ليل')], 'daytime': [o('نهار')], 'water': [o('ماء')],
    'prayer': [o('صلاة')], 'salah': [o('صلاة')], 'salat': [o('صلاة')], 'zakat': [o('زكاة')], 'zakah': [o('زكاة')],
    'charity': [o('صدقة', 'صَدَقَة')], 'sadaqa': [o('صدقة', 'صَدَقَة')], 'mercy': [o('رحمة')], 'patience': [o('صبر', 'صَبْر')],
    'light': [o('نور')], 'mind': [o('عقل')], 'reason': [o('عقل')], 'gold': [o('ذهب', 'ذَهَب')], 'thanks': [o('شكر', 'شُكْر')], 'gratitude': [o('شكر', 'شُكْر')],
    'calamity': [o('مصيبة')], 'messenger': [o('رسول')], 'prophet': [o('نبي')], 'book': [o('كتاب')], 'quran': [o('قرءان')],
    'benefit': [o('نفع', 'نَفْع')], 'corruption': [o('فساد')], 'good': [o('خير')], 'evil': [o('شر', 'شَرّ')],
    'punishment': [o('عذاب')], 'reward': [o('اجر'), o('ثواب')], 'hour': [o('ساعة')], 'resurrection': [o('قيامة')],
    'muslim': [o('مسلم')], 'jihad': [o('جهاد')], 'tongue': [o('لسان')], 'misguidance': [o('ضلال')], 'guidance': [o('هدي', 'هُدًى')],
    'female': [o('انثي')], 'male': [o('ذكر', 'ذَكَر')], 'remembrance': [o('ذكر', 'ذِكْر')],
    'soul': [o('نفس')], 'heart': [o('قلب', 'قَلْب')], 'knowledge': [o('علم', 'عِلْم')], 'truth': [o('حق', 'حَقّ')], 'falsehood': [o('باطل')],
    'peace': [o('سلام')], 'wealth': [o('مال')], 'money': [o('مال')], 'child': [o('ولد', 'وَلَد')], 'father': [o('اب', 'أَب')], 'mother': [o('ام', 'أُمّ')],
    'spouse': [o('زوج')], 'martyr': [o('شهيد')], 'witness': [o('شهيد')], 'repentance': [o('توبة')], 'forgiveness': [o('مغفرة')],
    'piety': [o('تقوي')], 'justice': [o('عدل', 'عَدْل')], 'injustice': [o('ظلم', 'ظُلْم')], 'poor': [o('فقير')], 'rich': [o('غني')],
    'good deeds': [o('صالحة', null, 'صلحت')], 'bad deeds': [o('سيئة')], 'this world': [o('دنيا')],
  };
  const PLURAL = { angels: 'angel', kings: 'king', devils: 'devil', gardens: 'garden', heavens: 'heaven', skies: 'sky', months: 'month', years: 'year',
    prophets: 'prophet', messengers: 'messenger', books: 'book', stars: 'star', seas: 'sea', prayers: 'prayer', souls: 'soul', hearts: 'heart',
    muslims: 'muslim', martyrs: 'martyr', witnesses: 'witness', females: 'female', males: 'male', children: 'child', fathers: 'father', mothers: 'mother',
    spouses: 'spouse', demons: 'devil', satans: 'devil', humans: 'human', lords: 'lord', kingdoms: 'kingdom', nights: 'night', rewards: 'reward' };

  // English meanings for the voweled lemmas that share a spelling, used to label the choices.
  const SENSES = {
    'مَلَك': 'angel', 'مُلْك': 'dominion', 'مَلِك': 'king', 'رَجُل': 'man', 'رِجْل': 'foot, leg', 'رَجِل': 'on foot',
    'جَنَّة': 'garden, paradise', 'جِنَّة': 'jinn, madness', 'جُنَّة': 'shield', 'بَرّ': 'land', 'بِرّ': 'righteousness',
    'سُنَّة': 'way, practice', 'سَنَة': 'year', 'سِنَة': 'slumber', 'آخِر': 'last, hereafter', 'آخَر': 'other', 'أَخَّرَ': 'to delay',
    'ذَهَب': 'gold', 'ذَهَبَ': 'to go', 'شُكْر': 'thanks', 'شَكَرَ': 'to thank', 'نَفْع': 'benefit', 'نَفَعَ': 'to benefit',
    'صَبْر': 'patience', 'صَبَرَ': 'to be patient', 'صَدَقَة': 'charity', 'رَبّ': 'Lord', 'هُدًى': 'guidance', 'هَدَى': 'to guide',
    'مَيِّت': 'dead', 'ذِكْر': 'remembrance', 'ذَكَرَ': 'to remember, mention', 'ذَكَر': 'male', 'حَقّ': 'truth, right', 'عِلْم': 'knowledge',
    'عَلِمَ': 'to know', 'عَلَّمَ': 'to teach', 'شَرّ': 'evil', 'وَلَد': 'child', 'أَب': 'father', 'أُمّ': 'mother', 'أَم': 'or',
    'قَلْب': 'heart', 'ظُلْم': 'injustice', 'ظَلَمَ': 'to wrong', 'عَدْل': 'justice', 'عَدَلَ': 'to act justly', 'بَشَر': 'human being',
    'بُشِّرَ': 'to be given good news', 'جِنّ': 'jinn',
  };

  // Arabic words that carry a claim's wording rather than its subject (all normalized).
  const AR_STOP = new Set(['كلمة', 'كلمه', 'لفظ', 'لفظة', 'لفظه', 'ذكر', 'ذكرت', 'يذكر', 'تذكر', 'ورد', 'وردت', 'يرد', 'ترد', 'تكرر', 'تكررت',
    'مرة', 'مره', 'مرات', 'القران', 'القرءان', 'قران', 'الكريم', 'في', 'مثل', 'نفس', 'العدد', 'عدد', 'بعدد', 'تساوي', 'يساوي', 'متساوي', 'متساويان',
    'كل', 'او', 'ثم', 'ايضا', 'اي', 'هي', 'هو', 'ان', 'انه', 'ذلك', 'هذا', 'هذه', 'قد', 'لقد', 'جاء', 'جاءت', 'عبارة', 'سورة', 'سوره', 'من', 'الي',
    'علي', 'عن', 'مع', 'بين', 'كما', 'حيث', 'تماما', 'بالضبط', 'فقط', 'و', 'ما', 'لا', 'كذلك', 'وكذلك', 'التي', 'الذي', 'حتي', 'وردتا', 'ذكرتا']);

  function cleanEnglish(t) { return ' ' + t.toLowerCase().replace(/[’‘`]/g, "'").replace(/[^a-z' ]+/g, ' ').replace(/\s+/g, ' ') + ' '; }

  // What an Arabic token in a claim refers to: the lemmas the corpus gives that written form (most
  // frequent first) and the form as the mushaf writes it, without leading clitics.
  const byCount = m => [...m.entries()].sort((a, b) => b[1] - a[1]).map(e => e[0]);
  // Leading clitics come off longest first (والملك -> ملك, like الملك), but only while what is left is the same
  // dictionary word: الله stays الله rather than becoming له ("to him").
  function stripClitic(ix, surf) {
    const own = ix.surfLemmas.get(surf);
    let best = surf;
    for (const p of PREFIXES) {
      if (!p || !surf.startsWith(p) || surf.length - p.length < 2) continue;
      const rest = surf.slice(p.length), theirs = ix.surfLemmas.get(rest);
      if (!ix.surfCount.has(rest) || (own && theirs && ![...own.keys()].some(l => theirs.has(l)))) continue;
      if (rest.length < best.length) best = rest;
    }
    return best;
  }
  // The dictionary words a set of written forms stand for: voweled senses where the index knows them.
  function sensesOf(ix, surfs) {
    const senses = new Map(), plain = new Map();
    for (const surf of surfs) {
      const fs = formSenses(ix, surf);
      if (fs) for (const [l, n] of fs) senses.set(l, (senses.get(l) || 0) + n);
      else for (const [l, n] of ix.surfLemmas.get(surf) || []) plain.set(l, (plain.get(l) || 0) + n);
    }
    const out = [];
    for (const [l, n] of senses) out.push({ opt: ix.VAR[normalize(l)] ? { norm: normalize(l), sense: l } : { norm: normalize(l) }, n });
    for (const [l, n] of plain) out.push({ opt: { norm: l }, n });
    return out.sort((a, b) => b.n - a.n).map(x => x.opt).slice(0, 8);
  }
  function resolveArabic(ix, tok) {
    const tries = [tok];
    for (const p of PREFIXES) if (p && tok.startsWith(p) && tok.length - p.length >= 2) tries.push(tok.slice(p.length));
    for (const t of tries) {
      const m = ix.surfLemmas.get(t);
      if (m && m.size) return { lemmas: byCount(m), options: sensesOf(ix, [t]), form: stripClitic(ix, t), respelled: false };
    }
    for (const t of tries) if (ix.lemmaCount.has(t)) {
      const form = citationForm(ix, t) || t;
      return { lemmas: [t], form, respelled: form !== t };
    }
    for (const t of tries) {
      const surfs = ix.skel.get(skeleton(t));
      if (!surfs) continue;
      const lemmas = new Map();
      for (const surf of surfs.keys()) for (const [l, n] of ix.surfLemmas.get(surf) || []) lemmas.set(l, (lemmas.get(l) || 0) + n);
      if (!lemmas.size) continue;
      const uth = byCount(surfs)[0];
      return { lemmas: byCount(lemmas), options: sensesOf(ix, [...surfs.keys()]), form: stripClitic(ix, uth), respelled: uth !== t };
    }
    return null;
  }

  // What the mushaf spelling of a word typed in modern spelling is, if they differ.
  function mushafSpelling(ix, q) {
    q = normalize(q);
    if (!q || ix.surfCount.has(q) || ix.lemmaCount.has(q) || ix.rootCount.has(q)) return null;
    const surfs = ix.skel.get(skeleton(q));
    return surfs ? byCount(surfs).slice(0, 3) : null;
  }

  // Every sense the lemmas can stand for, most frequent first (the claims engine's default), at most 8.
  function optionsFor(ix, lemmas) {
    const out = [];
    for (const norm of lemmas) {
      const vars = ix.VAR[norm];
      if (vars) vars.forEach(v => out.push({ norm, sense: v[0] }));
      else out.push({ norm });
    }
    return out.slice(0, 8);
  }

  // Pull the numbers and up to two words out of a claim, in English or Arabic.
  function parseClaim(ix, text) {
    const t = String(text || '').slice(0, 400);
    const numbers = (latinDigits(t).match(/\d+/g) || []).map(Number).filter(n => n > 0 && n < 100000).slice(0, 3);
    const words = [];
    const seen = new Set();
    const add = (source, text, options, form, respelled) => {
      const key = options.map(x => x.norm + '|' + (x.sense || '')).join(',');
      if (seen.has(key) || words.length >= 2) return;
      seen.add(key);
      words.push({ source, text, options, pick: 0, form: form || null, respelled: !!respelled });
    };
    let en = cleanEnglish(t);
    const keys = Object.keys(GLOSS).concat(Object.keys(PLURAL)).sort((a, b) => b.length - a.length);
    const hits = [];
    for (const k of keys) {
      const re = new RegExp(' ' + k + "(?:'s|')? ", 'g');
      let m;
      while ((m = re.exec(en))) { hits.push({ k, at: m.index }); en = en.slice(0, m.index) + ' '.repeat(m[0].length) + en.slice(m.index + m[0].length); }
    }
    hits.sort((a, b) => a.at - b.at).forEach(h => {
      const g = GLOSS[h.k] ? h.k : PLURAL[h.k];
      add('en', h.k, GLOSS[g].map(x => ({ ...x })));
    });
    const tokens = normalize(t).match(/[ء-ي]{2,}/g) || [];
    for (const tok of tokens) {
      if (AR_STOP.has(tok)) continue;
      const r = resolveArabic(ix, tok);
      if (!r || AR_STOP.has(r.lemmas[0])) continue;
      add('ar', tok, r.options && r.options.length ? r.options : optionsFor(ix, r.lemmas), r.form, r.respelled);
    }
    return { numbers, words };
  }

  // The three ways of counting one sense of a word.
  function countOption(ix, opt, form) {
    const v = opt.sense && (ix.VAR[opt.norm] || []).find(x => canon(x[0]) === canon(opt.sense));
    const lemma = v ? v[1] : ix.lemmaCount.get(opt.norm) || 0;
    const rootKey = v ? v[2] : ix.lemmaRoot.get(opt.norm) || '';
    const formText = form || opt.form || citationForm(ix, opt.norm) || opt.norm;
    return {
      form: formCount(ix, formText),
      formText,
      formOthers: formOthers(ix, formText, opt),   // of those, words that only share the spelling
      lemma,
      root: rootKey,
      rootCount: rootKey ? ix.rootCount.get(rootKey) || 0 : null,
    };
  }

  // Which counting methods land on a claimed number, and how close the nearest one comes.
  function judge(counts, claimed) {
    const methods = [['form', counts.form], ['lemma', counts.lemma], ['root', counts.rootCount]].filter(m => m[1] != null);
    const exact = methods.filter(m => m[1] === claimed).map(m => m[0]);
    const nearest = methods.slice().sort((a, b) => Math.abs(a[1] - claimed) - Math.abs(b[1] - claimed))[0];
    return { claimed, exact, nearest: nearest ? { method: nearest[0], value: nearest[1], diff: nearest[1] - claimed } : null };
  }

  const SENSE_EN = new Map(Object.entries(SENSES).map(([k, v]) => [canon(k), v]));
  function optionLabel(opt) {
    const main = opt.sense || opt.norm;
    const en = opt.sense && SENSE_EN.get(canon(opt.sense));
    return en ? `${main} (${en})` : main;
  }

  // ---- which page answers a question ----

  const ROUTES = {
    auditor: ['claim', 'claims', 'miracle', 'appears', 'mentioned', 'times', 'count of', 'occurs', 'مزعوم', 'مرة', 'مرات', 'اعجاز', 'ذكرت', 'وردت'],
    search: ['find', 'search', 'where does', 'word', 'occurrence', 'concordance', 'ابحث', 'بحث', 'كلمة', 'مواضع'],
    reader: ['read', 'recite', 'text of', 'mushaf', 'verse by verse', 'اقرا', 'قراءة', 'مصحف', 'تلاوة'],
    overview: ['how many surahs', 'how many verses', 'how many words', 'total', 'statistics', 'longest', 'shortest', 'كم عدد', 'احصاء', 'اطول', 'اقصر'],
    word: ['most common', 'most frequent', 'frequency', 'frequent words', 'lemma', 'الاكثر', 'تكرارا', 'جذع'],
    letters: ['letter', 'letters', 'alphabet', 'حرف', 'حروف'],
    mecca: ['meccan', 'medinan', 'mecca', 'makka', 'medina', 'madina', 'revealed where', 'مكي', 'مدني', 'مكة', 'المدينة'],
    emotion: ['emotion', 'mercy', 'hope', 'warning', 'tone', 'feeling', 'رحمة', 'تحذير', 'عاطف'],
    pronouns: ['pronoun', 'royal we', 'say we', 'says we', 'refers to himself', 'ضمير', 'نحن'],
    science: ['science', 'scientific', 'embryo', 'cosmos', 'universe', 'علم', 'علمي', 'الكون'],
    abjad: ['abjad', 'gematria', 'numerical value', 'jummal', 'ابجد', 'الجمل'],
    n19: ['19', 'nineteen', 'تسعة عشر'],
    structural: ['structure', 'surah numbers', 'verse counts', 'بنية', 'ترتيب'],
    symmetry: ['symmetry', 'pairs', 'equal', 'balance', 'same number', 'تناظر', 'ازواج', 'تساوي', 'توازن'],
    kg: ['map', 'graph', 'connections', 'network', 'related', 'خريطة', 'شبكة', 'علاقات'],
    stories: ['story', 'stories', 'prophet', 'moses', 'musa', 'yusuf', 'joseph', 'noah', 'nuh', 'abraham', 'ibrahim', 'jesus', 'pharaoh', 'قصة', 'قصص', 'نبي', 'موسي', 'يوسف', 'نوح', 'ابراهيم', 'فرعون'],
    lessons: ['lesson', 'lessons', 'advice', 'teach', 'moral', 'how should i', 'درس', 'دروس', 'نصيحة', 'عبرة'],
    duas: ['dua', "du'a", 'duaa', 'supplication', 'prayer for', 'pray for', 'دعاء', 'ادعية', 'ادعو'],
    tafsir: ['tafsir', 'commentary', 'scholar', 'explanation', 'interpret', 'تفسير', 'مفسر', 'بصائر'],
    untranslatable: ['translate', 'translation', 'untranslatable', 'meaning of the word', 'ترجمة', 'معني'],
    tawafuq: ['tawafuq', 'page alignment', 'mushaf pages', 'توافق'],
    alifi: ['alifi', 'every line', 'الالفي', 'الفي'],
    classifier: ['machine learning', 'classifier', 'predict', 'model', 'ai', 'تعلم الالة', 'تصنيف', 'نموذج'],
    stats: ['t-test', 'significant', 'significance', 'hypothesis', 'statistical test', 'اختبار', 'فرضية'],
    cluster: ['cluster', 'similar surahs', 'similar', 'pca', 'group', 'تجميع', 'متشابهة'],
    coincidence: ['coincidence', 'chance', 'probability', 'random', 'monte carlo', 'صدفة', 'مصادفة', 'احتمال'],
    hifz: ['memorise', 'memorize', 'memorization', 'memorisation', 'hifz', 'hafiz', 'حفظ', 'تحفيظ'],
    dashboard: ['dashboard', 'filter', 'bi ', 'لوحة'],
  };

  // Keyword test on word boundaries. Latin keys of five letters or more also match longer words
  // (predict -> prediction); shorter ones must stand alone. Arabic keys may carry a leading clitic;
  // keys of four letters or more may also carry a suffix, shorter ones only a pronoun suffix.
  const esc = x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const AR_LETTER = /[ء-ي]/;
  function keyRe(k) {
    if (AR_LETTER.test(k)) {
      const tail = k.length >= 4 ? '' : '(?:ي|ك|ه|ها|نا|هم|كم)?(?:\\s|$)';
      return new RegExp('(?:^|\\s)(?:و|ف|ب|ل|ال|وال|بال|فال|لل)?' + esc(k) + tail);
    }
    const key = k.trim();
    return new RegExp('(?:^|[^a-z])' + esc(key) + (key.length >= 5 ? '' : '(?:e?s)?(?:[^a-z]|$)'));
  }
  const KEY_RE = new Map();
  function hasKey(lower, norm, k) {
    let re = KEY_RE.get(k);
    if (!re) KEY_RE.set(k, (re = keyRe(k)));
    return re.test(AR_LETTER.test(k) ? norm : lower);
  }
  const prepText = t => ({ lower: ' ' + String(t || '').toLowerCase().replace(/[’‘`]/g, "'") + ' ',
    norm: ' ' + normalize(t).replace(/[^ء-ي0-9 ]+/g, ' ') + ' ' });

  function routeLocal(text, ix, meta) {
    const raw = String(text || '').slice(0, 200);
    const { lower, norm } = prepText(raw);
    const shortcut = surahShortcut(raw, meta) || claimShortcut(raw, ix) || wordShortcut(raw, ix);
    const scores = {};
    for (const [view, keys] of Object.entries(ROUTES)) {
      let sc = 0;
      for (const k of keys) if (hasKey(lower, norm, k)) sc += k.trim().length > 5 ? 2 : 1;
      if (sc) scores[view] = sc;
    }
    const ranked = Object.entries(scores).sort((a, b) => b[1] - a[1]).map(([view, score]) => ({ view, score }));
    return { shortcut, ranked };
  }

  function nameKey(s) { return s.toLowerCase().replace(/^(al|an|as|ash|at|ad|az|ar|aal)[- ]/, '').replace(/[^a-z]/g, ''); }
  function surahShortcut(raw, meta) {
    if (!meta || !meta.length) return null;
    const lower = raw.toLowerCase();
    const mentionsSurah = /\b(surah|surat|sura|chapter)\b/.test(lower) || /سور[ةه]/.test(raw);
    const num = latinDigits(raw).match(/\b(\d{1,3})\b/);
    if (mentionsSurah && num && +num[1] >= 1 && +num[1] <= 114) return { view: 'reader', s: +num[1] };
    const words = lower.replace(/[^a-zء-ي' -]+/g, ' ');
    const enTokens = words.match(/[a-z']+(?:-[a-z']+)*/g) || [];
    const arText = normalize(raw).replace(/[ة]/g, 'ه');
    const onlyName = raw.trim().split(/\s+/).length <= 3;
    if (!mentionsSurah && !onlyName) return null;
    for (const m of meta) {
      const k = nameKey(m.en);
      const arName = normalize(m.ar).replace(/[ة]/g, 'ه');
      const arBare = arName.replace(/^ال/, '');
      const enHit = k.length >= 3 && enTokens.some(t => { const tk = nameKey(t); return tk === k || tk === k + 'h' || tk + 'h' === k; });
      const arHit = arName.length >= 3 && (new RegExp('(^|\\s)(ال)?' + arBare + '(\\s|$)').test(arText));
      if (enHit || arHit) return { view: 'reader', s: m.n };
    }
    return null;
  }
  function claimShortcut(raw, ix) {
    if (!ix) return null;
    const p = parseClaim(ix, raw);
    return p.numbers.length && p.words.length ? { view: 'auditor', claim: raw.trim() } : null;
  }
  function wordShortcut(raw, ix) {
    const toks = normalize(raw).match(/[ء-ي]+/g) || [];
    if (toks.length !== 1 || /[a-z0-9]/i.test(raw.replace(/[؀-ۿ\s]/g, '').trim() || '')) return null;
    const hasIt = !ix || ix.surfCount.has(toks[0]) || ix.lemmaCount.has(toks[0]) || [...PREFIXES].some(p => p && ix.surfCount.has(p + toks[0]));
    return hasIt ? { view: 'search', q: toks[0] } : null;
  }

  // ---- which kind of du'a or lesson fits a situation ----

  const SITUATIONS = {
    duas: {
      protection: ['afraid', 'fear', 'scared', 'anxious', 'anxiety', 'worried', 'worry', 'panic', 'danger', 'unsafe', 'evil', 'harm', 'nightmare', 'envy', 'evil eye', 'enemy', 'threat', 'protect',
        'خوف', 'خائف', 'اخاف', 'قلق', 'قلقة', 'حماية', 'شر', 'حسد', 'عين', 'امان', 'كوابيس'],
      forgiveness: ['sin', 'sinned', 'guilt', 'guilty', 'regret', 'mistake', 'forgive', 'repent', 'ashamed', 'shame', 'wrong',
        'ذنب', 'ذنوب', 'توبة', 'اتوب', 'مغفرة', 'ندم', 'اخطات', 'خطا', 'استغفار'],
      guidance: ['confused', 'decision', 'decide', 'choose', 'choice', 'feel lost', 'direction', 'guidance', 'path', 'unsure', 'doubt', 'istikhara',
        'حيرة', 'محتار', 'قرار', 'هداية', 'ضائع', 'طريق', 'استخارة', 'اختيار'],
      provision: ['job', 'work', 'money', 'debt', 'poor', 'rent', 'bills', 'income', 'business', 'rizq', 'children', 'child', 'pregnant', 'baby', 'fertility', 'marriage',
        'رزق', 'عمل', 'وظيفة', 'مال', 'دين', 'ديون', 'فقر', 'اولاد', 'ذرية', 'حمل', 'زواج'],
      praise: ['grateful', 'thankful', 'thanks', 'happy', 'blessed', 'gratitude', 'praise', 'celebrate', 'success', 'passed',
        'شكر', 'حمد', 'سعيد', 'ممتن', 'نعمة', 'نجحت'],
      prophet: ['sad', 'grief', 'grieving', 'lonely', 'alone', 'hardship', 'trial', 'sick', 'ill', 'illness', 'pain', 'distress', 'depressed', 'broken', 'loss', 'lost someone', 'tired',
        'حزن', 'حزين', 'وحيد', 'وحدة', 'مرض', 'مريض', 'الم', 'كرب', 'ضيق', 'غم', 'ابتلاء', 'فقدت'],
      believer: ['parents', 'family', 'akhirah', 'hereafter', 'patience', 'steadfast', 'firm', 'faith', 'heart',
        'والدين', 'ثبات', 'صبر', 'الاخرة', 'قلب'],
    },
    lessons: {
      faith: ['doubt', 'believe', 'belief', 'faith', 'god', 'unseen', 'purpose', 'meaning of life', 'ايمان', 'شك', 'عقيدة', 'غيب'],
      ethics: ['honest', 'honesty', 'lie', 'lying', 'cheat', 'cheating', 'justice', 'fair', 'trust', 'promise', 'صدق', 'كذب', 'غش', 'عدل', 'امانة', 'وعد'],
      social: ['friend', 'friends', 'neighbour', 'neighbor', 'community', 'people', 'conflict', 'argument', 'colleague', 'society', 'اصدقاء', 'صديق', 'جار', 'جيران', 'مجتمع', 'خلاف', 'الناس'],
      worship: ['prayer', 'pray', 'fasting', 'ramadan', 'salah', 'quran', 'worship', 'mosque', 'صلاة', 'صيام', 'رمضان', 'عبادة', 'مسجد'],
      character: ['anger', 'angry', 'patience', 'patient', 'arrogant', 'arrogance', 'humble', 'jealous', 'envy', 'pride', 'self-control', 'temper',
        'غضب', 'صبر', 'كبر', 'تواضع', 'غيرة', 'حسد'],
      consequences: ['consequence', 'punishment', 'reward', 'deeds', 'karma', 'judgment', 'accountable', 'عاقبة', 'عقاب', 'جزاء', 'حساب'],
      knowledge: ['study', 'studying', 'learn', 'learning', 'exam', 'exams', 'school', 'university', 'knowledge', 'think', 'علم', 'دراسة', 'امتحان', 'تعلم', 'مدرسة', 'جامعة'],
      family: ['parents', 'mother', 'mom', 'father', 'dad', 'marriage', 'married', 'wife', 'husband', 'divorce', 'children', 'kids', 'son', 'daughter', 'family',
        'والدين', 'امي', 'ابي', 'والدتي', 'والدي', 'زواج', 'زوجة', 'زوج', 'طلاق', 'اولاد', 'ابن', 'ابنة', 'اسرة', 'عائلة'],
    },
  };

  function situationLocal(text, lib) {
    const table = SITUATIONS[lib];
    if (!table) return [];
    const { lower, norm } = prepText(text);
    const out = [];
    for (const [cat, keys] of Object.entries(table)) {
      const matched = keys.filter(k => hasKey(lower, norm, k));
      if (matched.length) out.push({ cat, score: matched.length, weight: matched.join('').length, matched });
    }
    return out.sort((a, b) => b.score - a.score || b.weight - a.weight);
  }

  // Words that mean someone may be at risk. The site shows a safety note first and does not send the
  // text to Jev.
  const CRISIS = /\b(suicid\w*|kill (my ?self|me)|end (my life|it all)|take my (own )?life|(?:want|wanna) to die(?! (?:my|your|his|her|the) (?:hair|clothes|shirt))|wanna die|don'?t want to (live|be alive)|self[- ]?harm\w*|hurt(ing)? my ?self|cut(ting)? my ?self|no reason to live|better off dead)\b|انتحار|انتحر|اقتل نفسي|أقتل نفسي|انهي حياتي|أنهي حياتي|اريد ان اموت|أريد أن أموت|ايذاء نفسي|إيذاء نفسي|اؤذي نفسي|أؤذي نفسي/i;
  function crisis(text) { return CRISIS.test(String(text || '')) || CRISIS.test(normalize(text)); }

  const api = { normalize, canon, skeleton, mushafSpelling, citationForm, formSenses, formOthers, endpoint, decide, trust, makeIndex, formCount, modeCounts, parseClaim, countOption, judge, optionLabel,
    routeLocal, situationLocal, crisis, GLOSS, PLURAL, SENSES, ROUTES, SITUATIONS, AR_STOP };
  root.QTA_JEV = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
