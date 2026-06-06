# -*- coding: utf-8 -*-
"""Statistical + ML compute layer - the Master of Business Analytics techniques
applied to the corpus. Everything is computed here (verified, testable) and the
frontend just renders the results.

Covers:
  - Hypothesis test (MIS771): Welch t-test, Meccan vs Medinan verse length
  - Linear regression (MIS771): verse length ~ structural features
  - Logistic classification (MIS771/772/710): Meccan vs Medinan from lemma TF-IDF
  - k-means clustering + PCA (MIS710/772): group surahs
  - TF-IDF cosine similarity (NLP): nearest surahs
"""
import numpy as np
from collections import Counter
from scipy import stats
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


def build(words, surah_meta):
    meta = {m['n']: m for m in surah_meta}

    # ---- verse-level table ----
    vlen = Counter()
    for w in words:
        vlen[(w['sura'], w['aya'])] += 1
    verses = []
    for (s, a), n in vlen.items():
        place = meta.get(s, {}).get('place', '')
        verses.append((s, a, n, 1 if place == 'Medina' else 0))
    V = np.array([[s, a, n, p] for (s, a, n, p) in verses], dtype=float)
    vn = V[:, 2]
    is_med = V[:, 3] == 1

    # ---- (1) Welch t-test: Meccan vs Medinan verse length ----
    mecca_len, med_len = vn[~is_med], vn[is_med]
    t, p = stats.ttest_ind(med_len, mecca_len, equal_var=False)
    # 95% CI of the mean difference (Welch)
    m1, m2 = med_len.mean(), mecca_len.mean()
    s1, s2 = med_len.var(ddof=1), mecca_len.var(ddof=1)
    n1, n2 = len(med_len), len(mecca_len)
    se = np.sqrt(s1 / n1 + s2 / n2)
    df = (s1 / n1 + s2 / n2) ** 2 / ((s1 / n1) ** 2 / (n1 - 1) + (s2 / n2) ** 2 / (n2 - 1))
    tc = stats.t.ppf(0.975, df)
    diff = m1 - m2
    ttest = {
        'meccanMean': round(m1 if False else mecca_len.mean(), 2),
        'medinanMean': round(med_len.mean(), 2),
        'diff': round(diff, 2), 't': round(float(t), 3), 'df': round(float(df), 1),
        'p': float(p), 'ci': [round(diff - tc * se, 2), round(diff + tc * se, 2)],
        'alpha': 0.05, 'reject': bool(p < 0.05),
    }

    # ---- (2) Linear regression: verse length ~ surah#, place, position ----
    pos_in_surah = {}
    for s, a, n, p in verses:
        pos_in_surah.setdefault(s, []).append(a)
    Xr = np.column_stack([V[:, 0], V[:, 3], V[:, 1]])  # surah#, place, ayah#
    yr = vn
    lr = LinearRegression().fit(Xr, yr)
    reg = {
        'r2': round(float(lr.score(Xr, yr)), 4),
        'intercept': round(float(lr.intercept_), 3),
        'coef': {'surahNumber': round(float(lr.coef_[0]), 4),
                 'medinanDummy': round(float(lr.coef_[1]), 3),
                 'ayahNumber': round(float(lr.coef_[2]), 4)},
        'n': int(len(yr)),
    }

    # ---- surah-level lemma documents for TF-IDF ----
    surah_lemmas = {}
    for w in words:
        if w['lemma']:
            surah_lemmas.setdefault(w['sura'], []).append(w['lemma'])
    nums = sorted(surah_lemmas)
    docs = [' '.join(surah_lemmas[n]) for n in nums]
    tfidf = TfidfVectorizer(token_pattern=r'[^ ]+', min_df=2)
    X = tfidf.fit_transform(docs)
    y = np.array([1 if meta[n]['place'] == 'Medina' else 0 for n in nums])

    # ---- (3) Logistic classification: Meccan vs Medinan (lemma TF-IDF) ----
    clf = LogisticRegression(max_iter=2000, C=1.0)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba = cross_val_predict(clf, X, y, cv=skf, method='predict_proba')[:, 1]
    pred = (proba >= 0.5).astype(int)
    cm = confusion_matrix(y, pred).tolist()
    clf.fit(X, y)
    vocab = np.array(tfidf.get_feature_names_out())
    coefs = clf.coef_[0]
    top_med = [{'w': vocab[i], 'c': round(float(coefs[i]), 3)} for i in np.argsort(coefs)[-8:][::-1]]
    top_mec = [{'w': vocab[i], 'c': round(float(coefs[i]), 3)} for i in np.argsort(coefs)[:8]]
    classifier = {
        'accuracy': round(float(accuracy_score(y, pred)), 4),
        'auc': round(float(roc_auc_score(y, proba)), 4),
        'baseline': round(float(max(y.mean(), 1 - y.mean())), 4),
        'confusion': cm,  # [[TN,FP],[FN,TP]] with 0=Meccan,1=Medinan
        'nMeccan': int((y == 0).sum()), 'nMedinan': int((y == 1).sum()),
        'topMedinan': top_med, 'topMeccan': top_mec,
    }

    # ---- (4) k-means clustering + PCA ----
    feats = np.array([[meta[n]['words'] / meta[n]['verses'], meta[n]['verses'],
                       meta[n]['words'], y[i]] for i, n in enumerate(nums)], dtype=float)
    Xs = StandardScaler().fit_transform(feats)
    K = 4
    km = KMeans(n_clusters=K, n_init=10, random_state=42).fit(Xs)
    coords = PCA(n_components=2, random_state=42).fit_transform(Xs)
    clusters = [{'n': nums[i], 'cluster': int(km.labels_[i]),
                 'x': round(float(coords[i, 0]), 3), 'y': round(float(coords[i, 1]), 3)}
                for i in range(len(nums))]

    # ---- (5) TF-IDF cosine similarity: nearest surahs ----
    Xn = X.toarray()
    Xn = Xn / (np.linalg.norm(Xn, axis=1, keepdims=True) + 1e-9)
    sim = Xn @ Xn.T
    np.fill_diagonal(sim, -1)
    similarity = {}
    for i, n in enumerate(nums):
        order = np.argsort(sim[i])[::-1][:5]
        similarity[str(n)] = [{'n': int(nums[j]), 's': round(float(sim[i, j]), 3)} for j in order]

    return {
        'ttest': ttest, 'regression': reg, 'classifier': classifier,
        'clusters': clusters, 'k': K, 'similarity': similarity,
    }
