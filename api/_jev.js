// Jev (TypeSafe AI) helpers shared by the /api/decide function and the batch jobs in data-build/jev.
//
// Jev answers typed questions about a piece of text ("state") with probabilities and a confidence,
// instead of writing prose. Every number the site shows is still computed from the corpus; Jev only
// decides things like which word a claim is about or which page a question belongs to.
'use strict';

const JEV_URL = process.env.JEV_URL || 'https://api.typesafe.ai/v1/systemone';
const JEV_MODEL = process.env.JEV_MODEL || 'jev-latest';

const choice = (instructions, criteria) => ({ type: 'choice', instructions, criteria });
const yesNo = (instructions, yes, no) => ({ type: 'noul', instructions, criteria: { true: yes, false: no } });

// One request, one answer per question key.
async function callJev(state, questions, { apiKey = process.env.TYPESAFE_API_KEY, timeoutMs = 8000 } = {}) {
  if (!apiKey) throw Object.assign(new Error('TYPESAFE_API_KEY is not set'), { status: 503 });
  const res = await fetch(JEV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: JEV_MODEL, state, questions }),
    signal: AbortSignal.timeout(timeoutMs),
  });
  if (!res.ok) {
    const err = new Error(`Jev returned HTTP ${res.status}`);
    err.status = res.status;
    err.detail = (await res.text().catch(() => '')).slice(0, 300);
    throw err;
  }
  const body = await res.json();
  const answers = {};
  for (const [key, q] of Object.entries(questions)) answers[key] = parseAnswer(q, (body.answers || {})[key]);
  return { model: body.model, answers, usage: body.usage };
}

// Normalise one answer to { value, confidence, probabilities }. Documented shapes: choice questions
// return { choice, probabilities, confidence }, score questions { score, legend, probabilities,
// confidence }, yes/no ("noul") questions a probability of yes. This is the one place to adjust if the
// live API differs. Unknown shapes come back as null, which callers treat as "Jev had no answer".
function parseAnswer(question, a) {
  if (!a || typeof a !== 'object') return null;
  const probs = a.probabilities && typeof a.probabilities === 'object' ? a.probabilities : null;
  const num = v => (typeof v === 'number' && isFinite(v) ? v : null);
  if (question.type === 'noul') {
    const p = [a.probability, a.p_true, a.yes, a.true, probs && probs.true, probs && probs.yes].map(num).find(v => v != null);
    if (p == null) return null;
    return { value: p >= 0.5, probability: p, confidence: num(a.confidence) ?? Math.abs(p - 0.5) * 2 };
  }
  let value = question.type === 'score' ? a.score : a.choice;
  if (value == null) value = a.value ?? a.answer ?? null;
  if (value == null && probs) value = Object.keys(probs).sort((x, y) => probs[y] - probs[x])[0] ?? null;
  if (value == null) return null;
  return { value, confidence: num(a.confidence) ?? (probs ? num(probs[value]) : null), probabilities: probs };
}

// ---- the decisions the public endpoint will make (nothing else can be asked through it) ----

const DESTINATIONS = {
  auditor: 'check famous claims that a word appears a certain number of times',
  search: 'find an Arabic word and every verse it appears in',
  reader: 'read a surah verse by verse with an English translation',
  overview: 'overall statistics: surahs, verses, words and roots',
  word: 'the most frequent words, lemmas and roots',
  letters: 'how often each Arabic letter occurs',
  mecca: 'compare surahs revealed in Mecca with those revealed in Medina',
  emotion: 'language of mercy, guidance, hope and warning',
  pronouns: 'how God refers to Himself: We, I and He',
  science: 'verses often cited in discussions about science',
  abjad: 'numerical (abjad) values of Arabic letters and words',
  n19: 'patterns claimed around the number 19',
  structural: 'patterns in surah numbers and verse counts',
  symmetry: 'pairs of words said to occur equally often, like life and death',
  kg: 'a map of connections between surahs, prophets and events',
  stories: 'stories of prophets and nations',
  lessons: 'lessons on faith, character, family and more',
  duas: 'prayers (du\'as) from the Quran',
  tafsir: 'insights from scholars on particular verses',
  untranslatable: 'Arabic words that translations struggle to capture',
  tawafuq: 'how words line up across the pages of the printed mushaf',
  alifi: 'a mushaf in which every line begins with the letter alif',
  classifier: 'machine learning that predicts whether a surah is Meccan or Medinan',
  stats: 'statistical tests on verse lengths',
  cluster: 'grouping surahs that are similar to each other',
  coincidence: 'how likely number coincidences are by chance',
  hifz: 'planning how to memorise the Quran',
  dashboard: 'filtering surahs by place of revelation and length',
};

const CATEGORIES = {
  duas: {
    protection: 'seeking refuge, safety or protection from harm, fear or evil',
    forgiveness: 'asking forgiveness for sins or mistakes',
    guidance: 'asking for guidance, the right path or the right decision',
    provision: 'asking for provision: sustenance, work, wealth or children',
    praise: 'praising and thanking God',
    believer: 'general prayers of the believers for this life and the next',
    prophet: 'prayers the prophets made in their own trials',
  },
  lessons: {
    faith: 'belief in God and the unseen',
    ethics: 'honesty, justice and right conduct',
    social: 'relations with other people and society',
    worship: 'prayer, fasting and devotion',
    character: 'patience, humility and self-control',
    consequences: 'the results of good and bad deeds',
    knowledge: 'learning, reflection and wisdom',
    family: 'parents, children and marriage',
  },
};

const LIMITS = { claim: 400, route: 200, situation: 300 };
const clean = s => (typeof s === 'string' ? s.replace(/[\u0000-\u001f\u007f]+/g, ' ').trim() : '');

// Validate a request body and turn it into { state, questions }, or { error }.
function buildRequest(body) {
  if (!body || typeof body !== 'object') return { error: 'expected a JSON body' };
  const kind = body.kind;
  if (!Object.prototype.hasOwnProperty.call(LIMITS, kind)) return { error: 'unknown kind' };
  const text = clean(body.text);
  if (!text) return { error: 'text is required' };
  if (text.length > LIMITS[kind]) return { error: `text is longer than ${LIMITS[kind]} characters` };

  if (kind === 'claim') {
    const cands = Array.isArray(body.candidates) ? body.candidates : [];
    if (cands.length > 10) return { error: 'at most 10 candidates' };
    const words = {};
    for (const c of cands) {
      const id = c && typeof c.id === 'string' && /^[a-z0-9_-]{1,24}$/i.test(c.id) ? c.id : null;
      const label = clean(c && c.label);
      if (!id || !label || label.length > 80) return { error: 'bad candidate' };
      words[id] = label;
    }
    const questions = {
      on_topic: yesNo('Is this a claim about how many times a word or words occur in the Quran?',
        'yes: it states or implies a count of how often a word occurs', 'no: it is about something else'),
      kind: choice('What kind of claim is this?', {
        single_word: 'how many times one word occurs',
        word_pair: 'two words said to occur the same number of times, or in a set ratio',
        number_19: 'a pattern built on the number 19',
        other: 'something else',
      }),
      method: choice('How does the claim count the word?', {
        exact_form: 'only this exact written form of the word',
        all_forms: 'the word in all its forms: singular, plural, with prefixes and suffixes',
        whole_root: 'every word built from the same three-letter root',
        unspecified: 'the claim does not say',
      }),
    };
    if (Object.keys(words).length > 1) questions.word = choice('Which Arabic word is the claim about?', words);
    return { kind, state: text, questions };
  }

  const onTopic = yesNo('Is this about the Quran, its words, verses, stories, prayers or teachings?',
    'yes: a question or request about the Quran or its content', 'no: unrelated to the Quran, spam or abuse');

  if (kind === 'route') {
    return { kind, state: text, questions: {
      on_topic: onTopic,
      page: choice('Which page of a Quran analytics website best answers this?', DESTINATIONS),
    } };
  }

  // situation
  const lib = body.lib;
  if (!Object.prototype.hasOwnProperty.call(CATEGORIES, lib)) return { error: 'unknown lib' };
  return { kind, state: text, questions: {
    on_topic: yesNo('Does this describe a situation, feeling or need that a prayer or a lesson could speak to?',
      'yes: it describes a situation, feeling or need', 'no: unrelated, spam or abuse'),
    category: choice(lib === 'duas' ? 'Which kind of prayer fits this situation best?' : 'Which kind of lesson fits this situation best?', CATEGORIES[lib]),
  } };
}

module.exports = { callJev, parseAnswer, buildRequest, choice, yesNo, DESTINATIONS, CATEGORIES, LIMITS, JEV_URL, JEV_MODEL };
