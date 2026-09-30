# Daleel discovery studies: pre-registration

Written and pushed on 29 September 2026, **before** any of the confirmatory analyses below were run.
The only analysis run beforehand was the pilot of study 1, described under that study. Everything here
is fixed: the data, the rules, the test and the threshold. Every result is reported, whether it holds or
not. Any change made after this file is logged under **Deviations** at the end, with its reason.

## Common ground

- **Text:** the Quranic Arabic Corpus morphology in `data-build/sources/quran-morphology.txt` (its SHA-256 is
  in `data-build/out/manifest.json`): 6,236 verses and 77,429 written words, rebuilt by `pipeline/corpus.py`.
  Each word has its written form, lemma, root and coarse part of speech (N, V, P) from its stem segment.
- **Normalization:** `pipeline.corpus.normalize` (vowel marks removed, ٱ آ أ إ → ا, ى → ي).
- **Content words:** words whose coarse part of speech is N or V and that carry a lemma.
- **Verse vectors:** TF-IDF over the lemmas of a verse's content words (scikit-learn, `min_df=2`,
  `sublinear_tf=True`, rows scaled to unit length), fitted on all 6,236 verses. Similarity is the cosine.
- **Threshold:** α = 0.05 for each primary test. Where a study has more than one primary test, Holm's
  correction is applied within the study. Exploratory results are labelled exploratory and carry no verdict.
- **Randomness:** every permutation uses the seed stated; the counts of permutations are fixed here.
- **Verdicts** on the site: "holds" (primary test passes), "does not hold" (it fails), "mixed" (a study's
  primary tests disagree), and "a map, not a test" for descriptive studies.

## 1. Do the names that close a verse fit the verse?

Classical scholars held that the pair of God's names closing a verse ("Forgiving, Merciful", "Mighty,
Wise", …) fits what the verse says.

- **Pilot (already run, 29 Sep 2026):** 212 verses in 48 surahs, 7 pairs with ≥ 10 verses, the ending's own
  roots removed. A model trained on other surahs guessed the ending 42.9% of the time against 33.5% for the
  commonest pair; none of 1,000 shuffles did as well. The pilot set the rules below; the confirmatory run
  widens the sample and adds a stricter test.
- **Sample:** verses of at least 4 words whose last two words are both nouns (coarse POS N) whose roots are in
  the list of divine-name roots below, with two different roots, the first of which is not قوم.
  Endings (ordered root pairs) with **at least 8 verses** form the classes.
  Divine-name roots: غفر رحم عزز حكم علم خبر سمع بصر قدر حمد غني رأف توب حلم كرم شكر ودد مجد لطف قوي عفو وسع
  شهد رقب وكل حفظ قهر ولي نصر قرب جيب حسب كبر علو عظم حقق بين وهب رزق فتح ملك قدس سلم أمن هيمن جبر خلق برأ
  صور حيي قوم وحد صمد أول أخر ظهر بطن برر جلل.
- **Features:** the lemmas of the words before the last two, leaving out any word whose root is one of the
  ending's two roots (so "forgive" cannot simply point to "Forgiving").
- **Model:** TF-IDF of those lemmas (`min_df=2`) and multinomial logistic regression (`C=3`, `max_iter=3000`),
  scored by accuracy under 5-fold cross-validation grouped by surah (a surah is never in both training and test).
- **Primary test A:** the endings shuffled across all verses, 2,000 times (seed 7). p = (shuffles at least as
  accurate + 1) / 2,001.
- **Primary test B (stricter):** the endings shuffled only among verses of the same surah, 2,000 times (seed 8),
  which keeps each surah's own mix of endings: it asks whether the verse itself, not just its surah, fits.
- **Reported:** accuracy, the commonest-pair baseline, both null distributions, both p (Holm), each pair's
  recall; exploratory: each pair's most telling words, and the 15 verses whose true ending the model found
  least likely (the "surprising endings").

## 2. Are long surahs built as mirrors (ring composition)?

Scholars such as Raymond Farrin have argued that al-Baqarah is a ring: its sections answer each other in
mirror order around a centre at 2:142–152 ("a middle nation", 2:143).

- **Unit:** the verse vector (common ground). Residual similarity of verses i and j:
  r(i, j) = s(i, j) − e(|i − j|), where e(d) is the mean of s over all pairs of the surah at distance d when
  d ≤ 20, and the mean over all pairs more than 20 verses apart otherwise. This removes the plain effect that
  nearby verses are alike, without letting a far pair be its own expectation.
- **Statistic:** the mean of r over the mirror pairs (i, n + 1 − i) whose distance is at least 2.
- **Primary test (al-Baqarah, 286 verses):** compared with the same statistic after rotating the verse order
  cyclically by every offset k = 1 … n − 1 (each rotation moves the mirror's centre elsewhere and keeps almost
  every verse next to its neighbours). One-sided p = (rotations at least as high + 1) / n.
- **Reported:** the statistic, its p, and (descriptive) the profile of the statistic for every possible centre
  c inside the surah with at least 30 mirror pairs; we report where that profile peaks and whether the peak
  falls within 2:130–2:160.
- **Exploratory scan:** every surah with at least 60 verses, the same test, with Benjamini–Hochberg at q = 0.10.

## 3. Does the rhyme change where the topic changes?

- **Rhyme of a verse:** from its last word, normalized: if the final letter is a consonant and the letter before
  it is ا, و or ي, the rhyme is that long vowel (with و and ي counted as one, as in ـون / ـين) plus the final
  consonant; otherwise it is the final letter alone.
- **Topic change at the boundary after verse b (inside one surah):** 1 − the cosine between the summed vectors of
  verses b−2 … b and of verses b+1 … b+3; only boundaries with three verses on each side inside the surah.
- **Statistic:** the mean topic change at boundaries where the rhyme changes minus the mean where it stays.
- **Primary test:** the rhyme-change marks shuffled among each surah's eligible boundaries (keeping each surah's
  count), 2,000 times (seed 11); one-sided p.
- **Reported:** the statistic, p; exploratory: the same split by Meccan and Medinan surahs, the share of each
  rhyme, and the longest runs of one rhyme.

## 4. Is each retelling of a story tuned to its own surah?

- **Tellings:** for each of Moses (with Pharaoh), Abraham, Noah, Lot, Hud, Salih and Shu'ayb, the verses that
  name him as a proper noun (the corpus's PN tag; for Moses, also verses naming Pharaoh). A surah's telling is
  all such verses in it; it needs at least 3 verses. A prophet enters the test if he has tellings in at least
  5 surahs.
- **Rest of the surah:** the surah's other verses, leaving out 3 verses on each side of every telling verse.
- **Statistic:** for each telling, the cosine between its summed vector and the summed vector of the rest of its
  own surah, minus the mean cosine with the rest of the other surahs that tell the same prophet's story;
  averaged over all tellings of all included prophets.
- **Primary test:** tellings reassigned to the other surahs of the same prophet at random (a random derangement
  within each prophet), 5,000 times (seed 13); one-sided p.
- **Reported:** the statistic, p; per prophet (exploratory); for Moses, each telling's most distinctive words.

## 5. Themes, and where they run (a map, not a test)

- Non-negative matrix factorization with **12 themes** on the verse vectors (`init='nndsvda'`,
  `random_state=0`, `max_iter=800`). A verse's theme is its largest weight, if that weight is above zero.
- **Stability:** refit with seeds 1 … 5 and match themes by cosine; only themes whose mean best-match cosine is
  at least 0.8 are named on the site. The names are our reading of each theme's top 10 words, and the words
  are shown beside them.
- **Reported:** each theme's top words, its share of verses, where it runs through the mushaf, each surah's mix.

## 6. Words that travel together (a map with a significance filter)

- Content lemmas with a root that occur in at least 20 verses. For each pair (different roots), the number of
  verses containing both; the one-sided Fisher exact test (hypergeometric) against independence; pointwise
  mutual information. Benjamini–Hochberg at q = 0.01 over all tested pairs.
- **Reported:** for each lemma, its strongest companions by PMI among significant pairs sharing at least
  3 verses.

## 7. The opening letters (al-ḥurūf al-muqaṭṭaʿa)

29 surahs open with disconnected letters (the corpus tags them INL).

- **7a. Are a surah's opening letters more frequent in it?** For each lettered surah and each distinct letter of
  its opening, that letter's share of all letters in the surah (normalized text, the opening letters themselves
  left out), and that share's percentile among the same letter's share in all 114 surahs (the fraction of
  surahs with a lower share, counting ties as half).
  **Statistic:** the mean percentile over all (surah, letter) cases.
  **Primary test:** the 29 letter sets reassigned to 29 surahs drawn at random without replacement, 10,000 times
  (seed 17); one-sided p. Reported per surah and letter as exploratory.
- **7b. Do surahs with the same opening share vocabulary?** Families: الم (2, 3, 29, 30, 31, 32), الر (10, 11,
  12, 14, 15), حم (40–46), طسم/طس (26, 27, 28). Similarity: the cosine between surah-level TF-IDF lemma vectors
  (the classifier's vectors, `data-build/pipeline/analytics.py`). **Statistic:** each family's mean
  within-family similarity, as a z-score against random sets of the same size, each member replaced by a
  surah drawn at random (without repeats) from those with the same Meccan or Medinan label and the same
  quartile of word count;
  **primary test:** the mean of the four z-scores against 10,000 simultaneous random draws (seed 19); one-sided p.
  **Secondary (reported, not a verdict):** for families of consecutive surahs (حم, طسم/طس), the rank of the
  family's similarity among all runs of the same number of consecutive surahs, which controls for the
  mushaf's habit of placing related surahs side by side.

## 8. Near-repeated verses (al-mutashābih al-lafẓī) (a map, not a test)

- Every pair of verses of at least 4 words whose lemma sequences are alike by at least 0.8
  (`difflib.SequenceMatcher` ratio) is listed with its differences; verses repeated word for word are grouped
  as refrains. **Reported:** the refrains and their counts, and the near pairs with the words that differ.

## 9. Style over the order of revelation

- **Order:** the traditional revelation order in the standard Egyptian edition, as tabulated in
  `scripts/enrich_quran_corpus.py` (`REV_ORDER`), checked to be a permutation of 1–114 whose ranks 87–114 are
  exactly the 28 surahs labelled Medinan.
- **Primary test:** the Spearman correlation between a surah's rank in that order and its mean verse length;
  **secondary (reported):** the same within the 86 Meccan surahs alone. p by 10,000 permutations (seed 23).
- **Reported:** both correlations; exploratory: the cumulative count of different words as the revelation
  proceeds, and each period's share of words used nowhere else.

## Deviations

1. **Study 5, before any run (29 Sep 2026).** The stability refits were to use seeds 1–5 with the same
   initialization, but `init='nndsvda'` is deterministic, so every refit would equal the first and the check
   would be empty. The refits use `init='random'` with seeds 1–5 instead; the main fit is unchanged.

## Afterwards (added on 29 September 2026, after the confirmatory runs)

The plan above is unchanged from commit `1a7b768` (with deviation 1 from `b5adb79`). The results are in
`web/discoveries.js`, written by `pipeline/discoveries.py`, and shown on the site's Discoveries pages. Corrections made
after publication are listed at the end; the table shows the corrected results.

| Study | Primary test | Result | Verdict |
|---|---|---|---|
| 1 | endings, shuffled across verses / within surahs | accuracy 0.3565 vs baseline 0.3087; p = 0.001 / 0.0075; Holm 0.002 / 0.0075 (corrected; first published as 0.001 / 0.004, see correction 1) | holds |
| 2 | al-Baqarah mirror vs 285 rotations | statistic 0.00384, p = 0.2552; profile peak at verse 231; scan: none passes BH | does not hold |
| 3 | rhyme change vs topic change, within-surah shuffles | difference 0.0063, p = 0.0005 | holds |
| 4 | retellings vs derangements | statistic 0.0361, p = 0.0002; own surah closer in 19 of 23 | holds |
| 5 | themes (map) | 10 of 12 themes stable (≥ 0.8) | a map |
| 6 | companions (map) | 1,207 of 86,945 pairs pass BH at q = 0.01 | a map |
| 7a | letters in their own surahs vs reassignments | mean percentile 0.5426, p = 0.0586 | does not hold |
| 7b | letter families vs matched draws | mean z 1.178, p = 0.0091 | holds |
| 8 | near repeats (map) | 74 refrains (208 verses), 217 near pairs | a map |
| 9 | Spearman, revelation order vs mean verse length | ρ = 0.669, p = 0.0001; Meccan only ρ = 0.515, p = 0.0001 | holds |

Added after the confirmatory runs, labelled exploratory on the site and carrying no verdict:

- **Study 3:** the same test with 2 and 4 verses on each side instead of 3 (1,000 permutations each, seeds 111 and 112):
  0.0068 (p = 0.001) and 0.0065 (p = 0.001).
- **Study 4:** the same test without Moses, which leaves Abraham's 9 tellings (5,000 derangements, seed 113): 0.0483, p = 0.0002.
- **All tested studies:** the null distributions are reported as histograms, with the number of shuffles that did at least as
  well as the text (`ge`), for the site's figures.

## Corrections after publication

1. **Study 1, the shuffle tests (found on 30 September 2026 by an automated code review, Codex, of the published
   code).** The features leave out the roots of each verse's own ending, so they depend on the ending. The published
   run built them once, from the true endings, and reused them in every shuffle. The shuffled copies therefore lacked
   the trace of the answer that the real features carry, and chance was set a little too low. The corrected run
   rebuilds the features, TF-IDF included, from the shuffled endings in every shuffle, with the same seeds; that is
   the test this plan describes. The observed accuracy does not change.

   | | Chance (mean of the shuffles), across verses / within surahs | p | Holm |
   |---|---|---|---|
   | Published | 0.2509 / 0.2764 | 0.001 / 0.004 | 0.002 / 0.004 |
   | Corrected | 0.2611 / 0.2862 | 0.001 / 0.0075 | 0.002 / 0.0075 |
   | Check: the 11 roots of the 9 pairs left out of every verse | 0.2506 / 0.2732 | 0.001 / 0.002 | 0.002 / 0.002 |

   The verdict stands: holds. The check, added with the correction and exploratory, keeps the features the same for
   every verse whatever its ending, so they can carry no trace of it; it scores the same accuracy, 0.3565. The
   exploratory «telling words» now come from the check's model, because the first lists partly reflected which words
   had been left out: تابَ, غَفَرَ and رَحْمَة are gone from them. The per-verse guesses, 5:38 and 5:118 among
   them, are unchanged.
2. **The results file (same review).** `python3 -m pipeline.discoveries --write` failed on a fresh checkout, after
   running every study, because `data-build/out/` is not in the repository. The folder is now created when missing.
   No result changed.

## Addendum A: the mirror claims, told apart (written on 30 September 2026, before any of it was run)

A reader pointed out that «al-Baqarah is a mirror» is said of three different things, and study 2 tested only a
verse-by-verse form of the first. This addendum adds a look at each claim. Study 2's own test and verdict are unchanged.
The sources were checked through search-engine extracts; the site says so where it cites them.

1. **A ring of sections around the qibla passage.** Raymond K. Farrin, «Surat al-Baqara: A Structural Analysis»,
   The Muslim World 100:1 (2010): 17–32, reads the surah as nine sections: A 1–20, B 21–39, C 40–103, D 104–141,
   E 142–152 (the centre), D′ 153–177, C′ 178–253, B′ 254–284, A′ 285–286.
   - **Measure:** each section is the sum of study 2's verse vectors (TF-IDF over the lemmas of content words, unit
     rows) over its verses, scaled to unit length; two sections' similarity is the cosine of their vectors.
   - **Statistic:** the sum of the cosines of the four pairs A–A′, B–B′, C–C′ and D–D′.
   - **Comparison:** the 24 ways to pair A, B, C and D one-to-one with A′, B′, C′ and D′. p is the share of the 24
     whose sum is at least the mirror's. The smallest possible p is 1/24 ≈ 0.042, so «holds» (p < 0.05) needs the
     mirror to be the best of all 24. Also reported: each pair's cosine and its rank among the four sections across
     the centre.
2. **The middle verse.** The observation (Farrin, interview, 2014; Muḥammad Jamīl al-Ḥabbāl, International
   Conference on the Numerical Miracle, Kuala Lumpur, 2012; popular talks) that 2:143, which calls the believers
   «a middle nation» (أمة وسطا), is the surah's middle verse. Descriptive only, no test:
   - the number of verses in the corpus's count and the two halves;
   - where «وسطا» falls among the surah's words (the corpus's tokens) and letters (the Arabic letters of each word
     as the corpus normalises them, no vowel marks), and where the middle word and the middle letter fall;
   - every word of the root و س ط in the Quran, and where it falls in its surah;
   - the number of verses in the other counting traditions, from the sources.
3. **A mirror inside Ayat al-Kursi (2:255).** Nine statements paired 1–9, 2–8, 3–7 and 4–6 around 5 («يعلم ما بين
   أيديهم وما خلفهم»), after Mehdi Azaiez, «The Throne Verse (āyat al-kursī) in Light of Rhetorical Analysis»
   (IQSA, 2013), and the popular nine-sentence reading. The statements are these word spans of 2:255 in the corpus:
   1–7, 8–12, 13–19, 20–26, 27–32, 33–40, 41–44, 45–47, 48–50.
   - **Measure:** the set of corpus roots in each statement (words without a root are left out); a pair's link is
     the number of roots the two share.
   - **Statistic:** the sum of the four pairs' links.
   - **Comparison:** the 24 ways to pair statements 1–4 with 6–9, with p as in 1.
   - **Exploratory only, with no verdict:** the structure was read from this very verse, so no chance baseline for it
     can be fair. The site shows the shared roots and describes the parallels of form in words.

