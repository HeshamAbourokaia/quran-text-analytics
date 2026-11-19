// How a word or a phrase typed in today's spelling is found in the mushaf's own. Used by Search in app.html, and
// loaded by the Node tests in data-build/tests.
//
// The text in words.js is the mushaf's (Uthmani) spelling, which often differs from today's. It leaves out alifs
// that today's spelling writes (ٱلْعَٰلَمِينَ for العالمين), writes the long alif as a hamza and an alif (ءَامَنُوا۟ for
// آمنوا), writes some long vowels as small letters (ٱلصَّلَوٰةَ for الصلاة), and joins the calling «يا» to the word it
// calls (يَٰمُوسَىٰ for يا موسى). Every word of the text is therefore also kept in today's spelling, and what is typed is
// compared with both. Vowel marks that are typed mean exactly as written, and a hamza that is typed must sit on the
// same seat, so «إن» is not «أن». Plain matching in the browser; nothing is sent anywhere.
(function (root) {
  'use strict';

  // ---- reading a spelling ----
  // the vowel marks and the small signs of the mushaf, which a comparison of spellings leaves out
  const TASHKEEL = /[ؐ-ًؚ-ٰٟۖ-ۭٓ-ٕ]/g;
  // Keyboards and copied text can bring Arabic «presentation forms»: one code point drawn as a ready-made shape, like
  // «ﷲ» (U+FDF2) that macOS types for الله. Compatibility normalization turns each back into its plain letters.
  const arPlain = s => String(s).replace(/[\uFB50-\uFDFF\uFE70-\uFEFC]/g, c => c.normalize('NFKC'));
  function normalize(s){
    if(!s) return '';
    s = arPlain(s).replace(/﻿/g,'').replace(TASHKEEL,'');
    s = s.replace(/[ٱآأإ]/g,'ا').replace(/ى/g,'ي');
    return s.trim();
  }
  // "As written" search. A word is cut into letters, each carrying its vowel marks. A hamza seat the reader typed
  // (أ إ آ ؤ ئ ء) must be that same seat, and every mark typed on a letter (fatha, damma, kasra, shadda, sukun,
  // tanween, the small alif) must be on that letter in the mushaf; letters typed bare accept any marks, and a bare
  // alif accepts any alif. "Exact word" compares the whole word; "Inside words" finds the letters anywhere in one.
  const AR_MARK1 = /[ؐ-ًؚ-ٰٟۖ-ۭ]/, AR_HAMZA = /[أإآؤئء]/;
  function arUnits(s){ const out=[]; for(const ch of arPlain(s||'').replace(/[ـ﻿]/g,'').normalize('NFC')){
    if(AR_MARK1.test(ch)){ if(out.length) out[out.length-1].m+=ch; } else if(!/\s/.test(ch)) out.push({b:ch, m:''}); } return out; }
  function arUnitEq(q, w){ let qb=q.b==='ٱ' ? 'ا' : q.b, wb=w.b==='ٱ' ? 'ا' : w.b; if(qb==='ى') qb='ي'; if(wb==='ى') wb='ي';
    if(AR_HAMZA.test(qb)){ if(qb!==wb) return false; } else if(qb==='ا'){ if(!/[اأإآ]/.test(wb)) return false; } else if(qb!==wb) return false;
    for(const m of q.m) if(!w.m.includes(m)) return false; return true; }
  function surfTest(raw, whole){
    const q=normalize(raw); if(!q) return null;
    const precise = !/\s/.test(raw.trim()) && (AR_HAMZA.test(raw) || AR_MARK1.test(raw));
    if(!precise) return whole ? (surf, norm)=>norm===q : (surf, norm)=>norm.includes(q);
    const qu=arUnits(raw);
    return (surf)=>{ const wu=arUnits(surf);
      if(whole) return wu.length===qu.length && qu.every((u,i)=>arUnitEq(u, wu[i]));
      for(let i=0;i+qu.length<=wu.length;i++){ let ok=true; for(let j=0;j<qu.length;j++) if(!arUnitEq(qu[j], wu[i+j])){ ok=false; break; } if(ok) return true; }
      return false; }; }
  // the long vowels the mushaf writes small (the dagger alif of ٱلْعَٰلَمِينَ) as the letters today's spelling writes
  const modernLetters = w => w.replace(/وٰ/g,'ا').replace(/ىٰ/g,'ى').replace(/ٰ/g,'ا')
    .replace(/ۦ(?=[\u0621-\u064A])/g,'ي').replace(/ۥ(?=[\u0621-\u064A])/g,'و');
  const modernSpelling = w => normalize(modernLetters(w));
  // the form two spellings are compared in: without the tatweel, and with «ءا» read as «ا»
  const key = s => normalize(s).replace(/ـ/g,'').replace(/ءا/g,'ا');
  // the same with every hamza kept on its seat (أ إ ؤ ئ ء), and, as a last resort, with the hamzas folded away
  const hamzaTyped = t => arPlain(t).replace(TASHKEEL,'').replace(/ـ/g,'').replace(/آ/g,'ءا').replace(/ٱ/g,'ا').replace(/ى/g,'ي');
  const hamzaModern = w => hamzaTyped(modernLetters(w));
  const hamzaFold = x => x.replace(/[ؤئء]/g,'').replace(/[أإآ]/g,'ا');
  // ---- every word of the text in today's spelling, built once for a word list (words.js) ----
  //   mod   without hamzas on the alif («آ» and «ءا» are both «ا»), for a word typed without hamzas
  //   ham   with every hamza on its seat, for a word typed with them
  //   fold  with the hamzas folded away, for a hamza typed on a seat the mushaf does not use for that word
  //         (إسرائيل for إسرءيل)
  //   lem   the dictionary words behind each of today's spellings, with how often
  //   as    the mushaf's commonest spelling of each of today's spellings (as words.js writes it, without marks)
  //   surf  that spelling with its marks, to show the reader
  let T = null;
  function tables(W){ if(T && T.W===W) return T; if(!W || !W.surface) return null;
    const mod=W.surface.map(w=>key(modernLetters(w))), ham=W.surface.map(hamzaModern), fold=ham.map(hamzaFold);
    const lem=new Map(), forms=new Map();
    for(let i=0;i<mod.length;i++){ const m=mod[i], l=W.lemma[i];
      if(l){ let a=lem.get(m); if(!a) lem.set(m, (a=new Map())); a.set(l, (a.get(l)||0)+1); }
      let f=forms.get(m); if(!f) forms.set(m, (f=new Map())); const k=W.norm[i]; let e=f.get(k); if(!e) f.set(k, (e={n:0, surf:W.surface[i]})); e.n++; }
    const as=new Map(), surf=new Map();
    for(const [m, f] of forms){ let best=null, bk=''; for(const [k, e] of f) if(!best || e.n>best.n){ best=e; bk=k; } as.set(m, bk); surf.set(m, best.surf); }
    return (T={W, mod, ham, fold, lem, as, surf}); }

  // «This exact word», as a test of a word's place in the list (i => true or false). With vowel marks typed: exactly as
  // the mushaf writes it. Without them the word is also compared in today's spelling: with its hamzas on the seats
  // that were typed, or, when no word of the mushaf is written that way, without them. whole: the word, whole;
  // otherwise the letters anywhere inside a word.
  function asWritten(W, raw, whole){ const st=surfTest(String(raw).replace(/آ/g,'ءا'), whole); if(!st || !W) return null;
    const base=i=>st(W.surface[i], W.norm[i]);
    if(AR_MARK1.test(raw) || /\s/.test(String(raw).trim())) return base;
    const X=tables(W);
    if(!AR_HAMZA.test(raw)){ const qm=key(raw); return whole ? i=>base(i) || X.mod[i]===qm : i=>base(i) || X.mod[i].includes(qm); }
    const hq=hamzaTyped(raw), exact = whole ? i=>base(i) || X.ham[i]===hq : i=>base(i) || X.ham[i].includes(hq);
    for(let i=0;i<W.surface.length;i++) if(exact(i)) return exact;
    const fq=hamzaFold(hq); return whole ? i=>X.fold[i]===fq : i=>X.fold[i].includes(fq); }

  // A word typed in today's spelling: the mushaf's commonest spelling of it (as), the same with its marks (surf), and
  // the dictionary word most often behind it (lemma, '' when it has none). null when no word is spelled that way today.
  function today(W, typed){ const X=tables(W), m=key(typed); if(!X || !X.as.has(m)) return null;
    const L=X.lem.get(m); let lemma='', best=0; if(L) for(const [l, c] of L) if(c>best){ best=c; lemma=l; }
    return {as:X.as.get(m), surf:X.surf.get(m), lemma}; }

  // A phrase: its words side by side, in this order, inside one verse. Gives the place of its first word each time it
  // comes (starts) and how many words of the text it spans (n). whole: each word exactly; otherwise the first word may
  // have letters before it and the last may have letters after it (واليوم الآخر for اليوم الآخر). A typed «يا» goes
  // with the word after it, since the mushaf writes the two as one (يَٰٓأَيُّهَا، يَٰمُوسَىٰ).
  function phrase(W, text, whole){ const X=tables(W);
    const typed=String(text||'').replace(/[«»"'().,،؛:!?؟]/g,' ').trim().split(/\s+/).filter(t=>normalize(t)), toks=[];
    for(let i=0;i<typed.length;i++){ if(normalize(typed[i])==='يا' && i+1<typed.length){ toks.push({t:typed[i]+typed[i+1], voc:true}); i++; } else toks.push({t:typed[i]}); }
    const n=toks.length, starts=[]; if(!n || !X) return {n, starts};
    const tests=toks.map((o,j)=>{ const tk=o.t, nq=key(tk);
      if(o.voc) return i=>X.mod[i]===nq;
      if(AR_MARK1.test(tk)) return asWritten(W, tk, true);            // vowel marks typed: this word exactly
      if(AR_HAMZA.test(tk)){ const hq=hamzaTyped(tk);                 // hamzas typed: on those seats
        if(!whole && j===0 && n>1) return i=>X.ham[i].endsWith(hq);
        if(!whole && j===n-1 && n>1) return i=>X.ham[i].startsWith(hq);
        return asWritten(W, tk, true); }
      if(!whole && j===0) return i=>W.norm[i].endsWith(nq) || X.mod[i].endsWith(nq);
      if(!whole && j===n-1) return i=>W.norm[i].startsWith(nq) || X.mod[i].startsWith(nq);
      return i=>W.norm[i]===nq || X.mod[i]===nq; });
    for(let i=0; i+n<=W.norm.length; i++){ if(!tests[0](i) || W.key[i+n-1]!==W.key[i]) continue;
      let ok=true; for(let j=1;j<n;j++) if(!tests[j](i+j)){ ok=false; break; }
      if(ok) starts.push(i); }
    return {n, starts}; }

  const api = { TASHKEEL, AR_MARK1, AR_HAMZA, arPlain, normalize, arUnits, arUnitEq, surfTest, modernLetters, modernSpelling,
    key, hamzaTyped, hamzaFold, tables, asWritten, today, phrase };
  root.QI_SPELL = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
