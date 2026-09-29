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

None yet.
