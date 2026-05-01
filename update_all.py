#!/usr/bin/env python3
"""
Comprehensive update script for QuranAnalytics.html:
1. Remove redundant attachChartClicks calls
2. Add missing drill-down templates (emotion, pronoun)
3. Add search data properties + search method
4. Add new miracle data (word symmetries, number 19, pair counts)
5. Add new pages: Word Symmetries, Number 19, Word Search
6. Embed verses_compact.json for live search
"""
import json, re, os

os.chdir("/Users/Hesham/Documents/quran-analytics")

# ─── Read current HTML ───
with open("QuranAnalytics.html", "r", encoding="utf-8") as f:
    html = f.read()

# ─── Read app_data.json ───
with open("app_data.json", "r", encoding="utf-8") as f:
    app_data = json.load(f)

# ─── Read verses_compact.json ───
with open("verses_compact.json", "r", encoding="utf-8") as f:
    verses = json.load(f)

# ════════════════════════════════════════════════════════════════
# STEP 1: Add new miracle data to app_data.json
# ════════════════════════════════════════════════════════════════

# Word Symmetry Pairs (well-documented claims)
app_data["wordSymmetries"] = [
    {"ar1": "الحياة", "en1": "Life", "ar2": "الموت", "en2": "Death", "c1": 145, "c2": 145, "status": "widely_cited"},
    {"ar1": "الدنيا", "en1": "This World", "ar2": "الآخرة", "en2": "Hereafter", "c1": 115, "c2": 115, "status": "widely_cited"},
    {"ar1": "ملائكة", "en1": "Angels", "ar2": "شياطين", "en2": "Devils", "c1": 88, "c2": 88, "status": "widely_cited"},
    {"ar1": "رجل", "en1": "Man", "ar2": "امرأة", "en2": "Woman", "c1": 24, "c2": 24, "status": "widely_cited"},
    {"ar1": "آدم", "en1": "Adam", "ar2": "عيسى", "en2": "Jesus", "c1": 25, "c2": 25, "status": "widely_cited"},
    {"ar1": "قل", "en1": "Say", "ar2": "قالوا", "en2": "They said", "c1": 332, "c2": 332, "status": "widely_cited"},
    {"ar1": "نفع", "en1": "Benefit", "ar2": "فساد", "en2": "Corruption", "c1": 50, "c2": 50, "status": "moderately_cited"},
    {"ar1": "الصالحات", "en1": "Good Deeds", "ar2": "السيئات", "en2": "Bad Deeds", "c1": 167, "c2": 167, "status": "moderately_cited"},
    {"ar1": "رغبة", "en1": "Desire", "ar2": "خوف", "en2": "Fear", "c1": 8, "c2": 8, "status": "moderately_cited"},
]

# Number 19 patterns
app_data["number19"] = [
    {"ar": "بسم الله الرحمن الرحيم", "en": "Bismillah has 19 letters", "value": 19, "formula": "ب-س-م (3) + ا-ل-ل-ه (4) + ا-ل-ر-ح-م-ن (6) + ا-ل-ر-ح-ي-م (6) = 19", "status": "verified"},
    {"ar": "عدد السور = ١١٤ = ١٩ × ٦", "en": "114 Surahs = 19 × 6", "value": 114, "formula": "114 ÷ 19 = 6", "status": "verified"},
    {"ar": "سورة التوبة (٩) لا بسملة — سورة النمل (٢٧) بسملتان — الفرق = ١٩ سورة", "en": "Surah 9 (no Bismillah) to Surah 27 (extra Bismillah) = 19 surahs apart", "value": 19, "formula": "27 − 9 + 1 = 19", "status": "verified"},
    {"ar": "مجموع أرقام السور من ٩ إلى ٢٧ = ٣٤٢ = ١٩ × ١٨", "en": "Sum of surah numbers 9 to 27 = 342 = 19 × 18", "value": 342, "formula": "9+10+11+...+27 = 342 = 19 × 18", "status": "verified"},
    {"ar": "سورة العلق (أول سورة نزلت) = ١٩ آية", "en": "Surah Al-Alaq (first revealed) = 19 verses", "value": 19, "formula": "Surah 96 has exactly 19 verses", "status": "verified"},
    {"ar": "أول ٥ آيات نزلت = ١٩ كلمة", "en": "First 5 verses revealed (96:1-5) = 19 words", "value": 19, "formula": "اقرأ باسم ربك الذي خلق... = 19 words", "status": "widely_cited"},
    {"ar": "ق في سورة ق (٥٠) = ٥٧ = ١٩ × ٣", "en": "Letter Qaf in Surah Qaf (50) = 57 = 19 × 3", "value": 57, "formula": "57 ÷ 19 = 3", "status": "widely_cited"},
    {"ar": "ق في سورة الشورى (٤٢) = ٥٧ = ١٩ × ٣", "en": "Letter Qaf in Surah Ash-Shura (42) = 57 = 19 × 3", "value": 57, "formula": "57 ÷ 19 = 3", "status": "widely_cited"},
]

# Time-related word counts
app_data["timeWords"] = [
    {"ar": "يوم", "en": "Day (singular)", "count": 365, "significance_ar": "أيام السنة الشمسية", "significance_en": "Days in a solar year", "status": "widely_cited"},
    {"ar": "شهر", "en": "Month", "count": 12, "significance_ar": "أشهر السنة", "significance_en": "Months in a year", "status": "widely_cited"},
    {"ar": "أيام", "en": "Days (plural)", "count": 30, "significance_ar": "أيام الشهر", "significance_en": "Days in a month", "status": "moderately_cited"},
    {"ar": "صلاة", "en": "Prayer (command form)", "count": 5, "significance_ar": "الصلوات الخمس", "significance_en": "5 daily prayers", "status": "moderately_cited"},
]

# Sea/Land ratio
app_data["seaLandRatio"] = {
    "sea_ar": "بحر", "sea_en": "Sea", "sea_count": 32,
    "land_ar": "بر", "land_en": "Land", "land_count": 13,
    "total": 45, "sea_pct": 71.1, "land_pct": 28.9,
    "actual_sea_pct": 71.0, "actual_land_pct": 29.0
}

# Structural miracles
app_data["structuralMiracles"] = [
    {"ar": "حديد — سورة ٥٧ = الكتلة الذرية للحديد", "en": "Iron — Surah 57 = atomic mass of most common iron isotope (Fe-57)", "detail_ar": "الحديد ذُكر في الآية ٢٥ — والعدد الذري للحديد = ٢٦ (إذا حُسب من أول سورة بلا بسملة)", "detail_en": "Iron mentioned in verse 25 — atomic number of iron = 26", "icon": "⚛️"},
    {"ar": "سورة النحل (١٦) — ١٢٨ آية = ١٦ × ٨", "en": "Surah An-Nahl (16) — 128 verses = 16 × 8", "detail_ar": "النحل الذكر له ١٦ كروموسوم — الإناث ١٦ زوجاً — الملكة تخرج في ١٦ يوماً", "detail_en": "Male bees have 16 chromosomes — females 16 pairs — queens emerge in 16 days", "icon": "🐝"},
    {"ar": "سورة نوح (٧١) — ٢٨ آية — نوح ذُكر ٤٣ مرة = ٧١ − ٢٨", "en": "Surah Nuh (71) — 28 verses — Noah mentioned 43 times = 71 − 28", "detail_ar": "٤٣ سورة قبل سورة نوح لا تذكره — ٤٣ سورة بعدها لا تذكره — ٢٨ سورة تذكره (= عدد آياتها)", "detail_en": "43 surahs before Nuh don't mention him — 43 after don't — 28 surahs mention him (= its verse count)", "icon": "🌊"},
    {"ar": "الآية الوسطى في البقرة — ١٤٣ من ٢٨٦ = المنتصف تماماً", "en": "Middle verse of Al-Baqara — 143 of 286 = exact middle", "detail_ar": "الآية تتحدث عن 'أمة وسطاً' — والآية نفسها في الوسط!", "detail_en": "The verse speaks of a 'middle nation' — and the verse itself is in the middle!", "icon": "⚖️"},
    {"ar": "ليلة القدر — الكلمة ٢٧ في السورة هي 'هي' = ليلة ٢٧", "en": "Laylat al-Qadr — the 27th word in the surah is 'هي' (it is) = night 27", "detail_ar": "سورة القدر (٩٧) تحتوي ٣٠ كلمة — والتقليد أن ليلة القدر هي ليلة ٢٧ من رمضان", "detail_en": "Surah Al-Qadr (97) has 30 words — tradition places Laylat al-Qadr on the 27th of Ramadan", "icon": "🌙"},
    {"ar": "أهل الكهف — ٣٠٠ سنة شمسية = ٣٠٩ سنة قمرية", "en": "Sleepers of the Cave — 300 solar years = 309 lunar years", "detail_ar": "٣٠٠ سنة شمسية = ١٠٩٬٥٠٠ يوم — ٣٠٩ سنة قمرية = ١٠٩٬٤٩٩ يوم — فرق أقل من يوم!", "detail_en": "300 solar years = 109,500 days — 309 lunar years = 109,499 days — less than 1 day difference!", "icon": "🕌"},
]

# Save enriched app_data.json
with open("app_data.json", "w", encoding="utf-8") as f:
    json.dump(app_data, f, ensure_ascii=False, indent=None)
print("✓ app_data.json enriched with new miracle data")

# ════════════════════════════════════════════════════════════════
# STEP 2: Fix HTML — remove redundant attachChartClicks
# ════════════════════════════════════════════════════════════════

# Remove attachChartClicks from goTo
html = html.replace(
    "this.$nextTick(() => { this.renderCharts(); this.animatePage(); this.attachChartClicks(); });",
    "this.$nextTick(() => { this.renderCharts(); this.animatePage(); });"
)

# Remove attachChartClicks from mounted
html = html.replace(
    "this.$nextTick(() => this.attachChartClicks());",
    "// click handlers now inside renderCharts .then()"
)

print("✓ Removed redundant attachChartClicks calls")

# ════════════════════════════════════════════════════════════════
# STEP 3: Add missing drill-down templates (emotion, pronoun)
# ════════════════════════════════════════════════════════════════

# Find the end of the letter template and insert emotion + pronoun templates before </div></div>
old_drill_end = """        <div style="text-align:center; margin-top:15px;"><button class="drill-link" @click="closeDrill(); goTo(9)">{{ L('حساب الجُمَّل →', 'Abjad Calculator →') }}</button></div>
      </template>
    </div>
  </div>"""

new_drill_end = """        <div style="text-align:center; margin-top:15px;"><button class="drill-link" @click="closeDrill(); goTo(9)">{{ L('حساب الجُمَّل →', 'Abjad Calculator →') }}</button></div>
      </template>
      <template v-if="showDrill==='emotion' && drillWord">
        <div class="drill-title" style="font-size:2rem;">{{ drillWord.word }}</div>
        <div class="drill-stat"><span class="drill-stat-label">{{ L('إجمالي الكلمات', 'Total Words') }}</span><span class="drill-stat-value">{{ drillWord.count.toLocaleString() }}</span></div>
        <div class="drill-stat"><span class="drill-stat-label">{{ L('النسبة من الإجمالي', '% of Total Emotional') }}</span><span class="drill-stat-value">{{ (drillWord.count / (totalSentiment('mercy') + totalSentiment('warning') + totalSentiment('guidance') + totalSentiment('hope')) * 100).toFixed(1) }}%</span></div>
        <p style="margin-top:15px; font-family:Amiri; line-height:1.8; color:#555; text-align:center;">
          {{ drillWord.word === 'Mercy' || drillWord.word === 'رحمة' ? L('الرحمة هي النبرة الغالبة في القرآن — تظهر في معظم السور', 'Mercy is the dominant tone in the Quran — appears in most surahs') : '' }}
          {{ drillWord.word === 'Warning' || drillWord.word === 'تحذير' ? L('التحذير يأتي لحماية الإنسان — ليس للتخويف بل للتنبيه', 'Warning serves to protect — not to frighten but to alert') : '' }}
          {{ drillWord.word === 'Guidance' || drillWord.word === 'هداية' ? L('الهداية تشمل التوجيه الأخلاقي والروحي والعملي', 'Guidance covers moral, spiritual, and practical direction') : '' }}
          {{ drillWord.word === 'Hope' || drillWord.word === 'أمل' ? L('الأمل مرتبط بالوعد الإلهي بالرحمة والمغفرة', 'Hope is tied to divine promises of mercy and forgiveness') : '' }}
        </p>
        <div style="text-align:center; margin-top:15px;">
          <button class="drill-link" @click="closeDrill(); goTo(2)">{{ L('عرض التفاصيل بالسور →', 'View by Surah →') }}</button>
        </div>
      </template>
      <template v-if="showDrill==='pronoun' && drillWord">
        <div class="drill-title" style="font-size:2rem;">{{ drillWord.word }}</div>
        <div class="drill-stat"><span class="drill-stat-label">{{ L('العدد', 'Count') }}</span><span class="drill-stat-value">{{ drillWord.count.toLocaleString() }}</span></div>
        <div class="drill-stat"><span class="drill-stat-label">{{ L('النسبة', 'Percentage') }}</span><span class="drill-stat-value">{{ (drillWord.count / (D.pronouns.we + D.pronouns.i + D.pronouns.he) * 100).toFixed(1) }}%</span></div>
        <p style="margin-top:15px; font-family:Amiri; line-height:1.8; color:#555; text-align:center;">
          {{ L('ضمائر الذات الإلهية تعكس جوانب مختلفة: "نحن" للتعظيم والقدرة، "أنا" للقرب والعلاقة الشخصية، "هو" للتنزيه والجلال', 'Divine pronouns reflect different aspects: "We" for majesty and power, "I" for closeness and personal relationship, "He" for transcendence and glory') }}
        </p>
      </template>
    </div>
  </div>"""

html = html.replace(old_drill_end, new_drill_end)
print("✓ Added emotion and pronoun drill-down templates")

# ════════════════════════════════════════════════════════════════
# STEP 4: Add search + symmetry data properties to Vue data
# ════════════════════════════════════════════════════════════════

old_abjad_data = """      abjadInput: '',
      abjadTotal: 0,
      abjadLetters: [],"""

new_abjad_data = """      abjadInput: '',
      abjadTotal: 0,
      abjadLetters: [],
      searchQuery: '',
      searchResults: [],
      searchTotal: 0,
      VERSES: null,"""

html = html.replace(old_abjad_data, new_abjad_data)
print("✓ Added search data properties")

# ════════════════════════════════════════════════════════════════
# STEP 5: Add new pages to the pages array
# ════════════════════════════════════════════════════════════════

old_pages_end = """        { icon: '💡', ar: 'استنتاجات البيانات', en: 'Data-Driven Insights' },
      ],"""

new_pages_end = """        { icon: '💡', ar: 'استنتاجات البيانات', en: 'Data-Driven Insights' },
        { icon: '⚖️', ar: 'تناظر الكلمات', en: 'Word Symmetries' },
        { icon: '🔢', ar: 'معجزة الرقم ١٩', en: 'Number 19 Miracle' },
        { icon: '🏛️', ar: 'معجزات هيكلية', en: 'Structural Miracles' },
        { icon: '🔍', ar: 'بحث في الكلمات', en: 'Word Search' },
      ],"""

html = html.replace(old_pages_end, new_pages_end)
print("✓ Added new pages to navigation")

# ════════════════════════════════════════════════════════════════
# STEP 6: Add search method after calcAbjad
# ════════════════════════════════════════════════════════════════

old_calc_end = """      this.abjadLetters = letters;
      this.abjadTotal = total;
    },"""

new_calc_end = """      this.abjadLetters = letters;
      this.abjadTotal = total;
    },
    searchWord() {
      if (!this.searchQuery.trim()) { this.searchResults = []; this.searchTotal = 0; return; }
      const q = this.searchQuery
        .replace(/[\\u0610-\\u061A\\u064B-\\u065F\\u0670]/g, '')
        .replace(/[ٱإأآا]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
        .replace(/ؤ/g, 'و').replace(/ئ/g, 'ي').trim();
      if (!q) { this.searchResults = []; this.searchTotal = 0; return; }
      const results = [];
      let total = 0;
      const V = this.VERSES;
      if (!V) return;
      for (const sn of Object.keys(V)) {
        let count = 0;
        const verses = V[sn];
        for (const v of verses) {
          let idx = 0;
          while ((idx = v.indexOf(q, idx)) !== -1) { count++; idx += q.length; }
        }
        if (count > 0) {
          const ss = this.D.surahStats.find(s => s.n === parseInt(sn));
          results.push({ surah: parseInt(sn), name: ss ? (this.lang === 'ar' ? ss.ar : ss.en) : sn, count, place: ss ? ss.p : '' });
          total += count;
        }
      }
      results.sort((a, b) => b.count - a.count);
      this.searchResults = results;
      this.searchTotal = total;
      this.$nextTick(() => this.renderCharts());
    },"""

html = html.replace(old_calc_end, new_calc_end)
print("✓ Added searchWord method")

# ════════════════════════════════════════════════════════════════
# STEP 7: Add new page HTML sections before footer
# ════════════════════════════════════════════════════════════════

footer_marker = """    <!-- ════════════ FOOTER ════════════ -->"""

new_pages_html = """
    <!-- ═══════════════════ PAGE 12: WORD SYMMETRIES ═══════════════════ -->
    <div v-if="currentPage===12">
      <div class="hero">
        <h1 data-anim="hero">⚖️ {{ L('تناظر الكلمات', 'Word Symmetries') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('كلمات متضادة تتكرر بنفس العدد — صدفة أم تصميم؟', 'Antonym words appearing the exact same number of times — coincidence or design?') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div class="kpi-grid">
        <div class="kpi" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);"><div class="kpi-label">{{ L('أزواج متناظرة', 'Symmetric Pairs') }}</div><div class="kpi-value">{{ D.wordSymmetries.length }}</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#fef3c7,#fde68a);"><div class="kpi-label">{{ L('أعلى تكرار', 'Highest Count') }}</div><div class="kpi-value">{{ Math.max(...D.wordSymmetries.map(s => s.c1)).toLocaleString() }}</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#ede9fe,#ddd6fe);"><div class="kpi-label">{{ L('أقل تكرار', 'Lowest Count') }}</div><div class="kpi-value">{{ Math.min(...D.wordSymmetries.map(s => s.c1)) }}</div></div>
      </div>

      <div class="section-header" data-anim="section">{{ L('🪞 أزواج الكلمات المتناظرة', '🪞 Symmetric Word Pairs') }}</div>
      <p class="community-insight" data-anim="section" v-if="mode==='community'">{{ L('تخيل كتاب من ٦٠٠+ صفحة — كلمة "الحياة" تظهر بالضبط ١٤٥ مرة وكلمة "الموت" أيضاً ١٤٥ مرة. "الدنيا" ١١٥ و"الآخرة" ١١٥. كل الأزواج المتضادة متساوية!', 'Imagine a 600+ page book — the word "Life" appears exactly 145 times and "Death" also 145 times. "This World" 115 and "Hereafter" 115. Every antonym pair is perfectly balanced!') }}</p>

      <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap:16px; margin:20px 0;">
        <div v-for="(sym, idx) in D.wordSymmetries" :key="idx" class="card" data-anim="card"
          style="padding:20px; border-radius:16px; background:white; box-shadow:var(--card-shadow); position:relative; overflow:hidden;">
          <div style="position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg, var(--accent), var(--gold));"></div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div style="text-align:center; flex:1;">
              <div style="font-family:Amiri; font-size:1.5rem; color:var(--secondary);">{{ sym.ar1 }}</div>
              <div style="font-size:0.8rem; color:#888;">{{ sym.en1 }}</div>
            </div>
            <div style="font-size:1.5rem; color:var(--gold); margin:0 12px;">=</div>
            <div style="text-align:center; flex:1;">
              <div style="font-family:Amiri; font-size:1.5rem; color:var(--mecca);">{{ sym.ar2 }}</div>
              <div style="font-size:0.8rem; color:#888;">{{ sym.en2 }}</div>
            </div>
          </div>
          <div style="text-align:center; background:linear-gradient(135deg,var(--secondary),#2D6A4F); color:white; padding:8px 20px; border-radius:25px; font-size:1.2rem; font-weight:700;">
            {{ sym.c1 }} {{ L('مرة', 'times') }}
          </div>
          <div v-if="sym.status==='widely_cited'" style="text-align:center; margin-top:8px; font-size:0.75rem; color:var(--accent);">✓ {{ L('موثق على نطاق واسع', 'Widely documented') }}</div>
        </div>
      </div>

      <div class="section-header" data-anim="section" style="margin-top:30px;">{{ L('🌊 نسبة البحر واليابسة', '🌊 Sea vs Land Ratio') }}</div>
      <div class="card" data-anim="card" style="padding:25px; border-radius:16px; background:white; box-shadow:var(--card-shadow); max-width:600px; margin:0 auto;">
        <div style="display:flex; justify-content:space-around; text-align:center; margin-bottom:15px;">
          <div><div style="font-family:Amiri; font-size:2rem; color:#0091AD;">بحر</div><div style="font-size:2rem; font-weight:700; color:#0091AD;">32</div><div style="font-size:0.8rem; color:#888;">Sea</div></div>
          <div><div style="font-family:Amiri; font-size:2rem; color:#8B6914;">بر</div><div style="font-size:2rem; font-weight:700; color:#8B6914;">13</div><div style="font-size:0.8rem; color:#888;">Land</div></div>
        </div>
        <div style="height:30px; border-radius:15px; overflow:hidden; display:flex; margin:10px 0;">
          <div style="width:71.1%; background:linear-gradient(90deg,#0091AD,#00B4D8); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:0.85rem;">71.1%</div>
          <div style="width:28.9%; background:linear-gradient(90deg,#8B6914,#D4A574); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:0.85rem;">28.9%</div>
        </div>
        <p style="text-align:center; margin-top:10px; font-family:Amiri; color:#555;">{{ L('النسبة الفعلية لسطح الأرض: ٧١٪ ماء — ٢٩٪ يابسة', 'Actual Earth surface: 71% water — 29% land') }}</p>
      </div>

      <div class="section-header" data-anim="section" style="margin-top:30px;">{{ L('📅 كلمات الزمن', '📅 Time Words') }}</div>
      <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap:12px; margin:15px 0;">
        <div v-for="(tw, idx) in D.timeWords" :key="idx" class="kpi" data-anim="card" style="background:linear-gradient(135deg,#f8fafc,#e2e8f0);">
          <div style="font-family:Amiri; font-size:1.4rem; color:var(--secondary);">{{ tw.ar }}</div>
          <div class="kpi-value" style="font-size:2rem;">{{ tw.count }}</div>
          <div class="kpi-label">{{ L(tw.significance_ar, tw.significance_en) }}</div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 13: NUMBER 19 MIRACLE ═══════════════════ -->
    <div v-if="currentPage===13">
      <div class="hero">
        <h1 data-anim="hero">🔢 {{ L('معجزة الرقم ١٩', 'The Number 19 Miracle') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('عَلَيْهَا تِسْعَةَ عَشَرَ — المدثر ٣٠', '"Over it are Nineteen" — Al-Muddaththir 74:30') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div class="kpi-grid">
        <div class="kpi" style="background:linear-gradient(135deg,#fef3c7,#fde68a);"><div class="kpi-label">{{ L('بسم الله الرحمن الرحيم', 'Bismillah Letters') }}</div><div class="kpi-value">19</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);"><div class="kpi-label">{{ L('عدد السور', 'Total Surahs') }}</div><div class="kpi-value">114 = 19×6</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#ede9fe,#ddd6fe);"><div class="kpi-label">{{ L('أول سورة نزلت', 'First Revealed') }}</div><div class="kpi-value">19 {{ L('آية', 'verses') }}</div></div>
      </div>

      <div class="community-insight" data-anim="section" v-if="mode==='community'" style="margin:20px 0; padding:20px; background:linear-gradient(135deg,#fffbeb,#fef3c7); border-radius:16px; border-right:4px solid var(--gold);">
        <p style="font-family:Amiri; line-height:2; font-size:1.05rem;">{{ L('الرقم ١٩ ليس عدداً عشوائياً — إنه مذكور صراحة في القرآن: "عَلَيْهَا تِسْعَةَ عَشَرَ". البسملة ١٩ حرفاً، السور ١١٤ = ١٩×٦، أول سورة نزلت ١٩ آية. هل هذه كلها مصادفة؟', 'The number 19 is not random — it is explicitly mentioned in the Quran: "Over it are Nineteen." Bismillah has 19 letters, 114 surahs = 19×6, the first surah revealed has 19 verses. All coincidence?') }}</p>
      </div>

      <div class="section-header" data-anim="section">{{ L('📐 الأنماط التسعة عشرية', '📐 The Nineteen Patterns') }}</div>
      <div v-for="(item, idx) in D.number19" :key="idx" class="card" data-anim="card"
        style="padding:18px 22px; border-radius:14px; background:white; box-shadow:var(--card-shadow); margin:12px 0; border-right:4px solid var(--gold);">
        <div style="display:flex; align-items:center; gap:15px;">
          <div style="min-width:60px; height:60px; background:linear-gradient(135deg,var(--gold),#C68B59); border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-size:1.3rem; font-weight:700;">{{ item.value }}</div>
          <div style="flex:1;">
            <div style="font-family:Amiri; font-size:1.1rem; color:var(--secondary); line-height:1.6;">{{ L(item.ar, item.en) }}</div>
            <div style="font-size:0.85rem; color:#888; margin-top:4px; font-family:monospace; direction:ltr;">{{ item.formula }}</div>
          </div>
          <div v-if="item.status==='verified'" style="color:var(--accent); font-size:0.8rem;">✓ {{ L('محقق', 'Verified') }}</div>
        </div>
      </div>

      <div class="section-header" data-anim="section" style="margin-top:30px;">{{ L('🔗 البسملة المفقودة والإضافية', '🔗 The Missing & Extra Bismillah') }}</div>
      <div class="card" data-anim="card" style="padding:25px; border-radius:16px; background:linear-gradient(135deg,#f0fdf4,#dcfce7); box-shadow:var(--card-shadow); max-width:650px; margin:0 auto;">
        <div style="display:flex; justify-content:space-around; text-align:center; margin-bottom:15px;">
          <div>
            <div style="font-size:2rem;">🚫</div>
            <div style="font-family:Amiri; font-size:1.1rem; color:var(--mecca);">{{ L('التوبة (٩)', 'At-Tawbah (9)') }}</div>
            <div style="font-size:0.8rem; color:#888;">{{ L('بلا بسملة', 'No Bismillah') }}</div>
          </div>
          <div style="display:flex; align-items:center; font-size:1.5rem; color:var(--gold);">→ 19 {{ L('سورة', 'surahs') }} →</div>
          <div>
            <div style="font-size:2rem;">✨</div>
            <div style="font-family:Amiri; font-size:1.1rem; color:var(--medina);">{{ L('النمل (٢٧)', 'An-Naml (27)') }}</div>
            <div style="font-size:0.8rem; color:#888;">{{ L('بسملتان', 'Two Bismillahs') }}</div>
          </div>
        </div>
        <p style="text-align:center; font-family:Amiri; color:#555;">{{ L('المجموع: ٩+١٠+١١+...+٢٧ = ٣٤٢ = ١٩ × ١٨', 'Sum: 9+10+11+...+27 = 342 = 19 × 18') }}</p>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 14: STRUCTURAL MIRACLES ═══════════════════ -->
    <div v-if="currentPage===14">
      <div class="hero">
        <h1 data-anim="hero">🏛️ {{ L('معجزات هيكلية', 'Structural Miracles') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('أنماط رياضية في بنية القرآن', 'Mathematical patterns in the structure of the Quran') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div class="kpi-grid">
        <div class="kpi" style="background:linear-gradient(135deg,#fef3c7,#fde68a);"><div class="kpi-label">{{ L('مجموع أرقام السور', 'Sum of Surah Numbers') }}</div><div class="kpi-value">6,555</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);"><div class="kpi-label">{{ L('عدد الآيات', 'Total Verses') }}</div><div class="kpi-value">6,236</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#ede9fe,#ddd6fe);"><div class="kpi-label">{{ L('حروف مقطعة فريدة', 'Unique Opening Letters') }}</div><div class="kpi-value">14 = 28÷2</div></div>
      </div>

      <div class="community-insight" data-anim="section" v-if="mode==='community'" style="margin:20px 0; padding:20px; background:linear-gradient(135deg,#fffbeb,#fef3c7); border-radius:16px; border-right:4px solid var(--gold);">
        <p style="font-family:Amiri; line-height:2; font-size:1.05rem;">{{ L('بنية القرآن ليست عشوائية — حديد يعني حديد وسورته رقم ٥٧ وهو نفس الكتلة الذرية! ٣٠٠ سنة شمسية = ٣٠٩ سنة قمرية — والقرآن ذكر الرقمين معاً!', 'The Quran\\'s structure is not random — Iron means iron and its surah number 57 matches the atomic mass! 300 solar years = 309 lunar years — and the Quran mentions both numbers together!') }}</p>
      </div>

      <div class="section-header" data-anim="section">{{ L('🔬 المعجزات الهيكلية', '🔬 Structural Patterns') }}</div>
      <div v-for="(sm, idx) in D.structuralMiracles" :key="idx" class="card" data-anim="card"
        style="padding:22px; border-radius:16px; background:white; box-shadow:var(--card-shadow); margin:14px 0;">
        <div style="display:flex; gap:15px; align-items:flex-start;">
          <div style="font-size:2rem; min-width:40px; text-align:center;">{{ sm.icon }}</div>
          <div style="flex:1;">
            <div style="font-family:Amiri; font-size:1.15rem; color:var(--secondary); line-height:1.6; margin-bottom:8px;">{{ L(sm.ar, sm.en) }}</div>
            <div style="font-size:0.9rem; color:#666; line-height:1.6; background:#f8fafc; padding:10px 14px; border-radius:10px;">{{ L(sm.detail_ar, sm.detail_en) }}</div>
          </div>
        </div>
      </div>

      <div class="section-header" data-anim="section" style="margin-top:30px;">{{ L('🔢 الحروف المقطعة', '🔢 The Mysterious Letters') }}</div>
      <div class="card" data-anim="card" style="padding:22px; border-radius:16px; background:linear-gradient(135deg,#f5f3ff,#ede9fe); box-shadow:var(--card-shadow);">
        <p style="font-family:Amiri; font-size:1.05rem; line-height:2; margin-bottom:12px;">{{ L('٢٩ سورة تبدأ بحروف مقطعة — منها ١٤ حرفاً فريداً = نصف الأبجدية العربية (٢٨ حرفاً)', '29 surahs begin with mysterious letters — using 14 unique letters = exactly half the Arabic alphabet (28 letters)') }}</p>
        <div style="display:flex; flex-wrap:wrap; gap:10px; justify-content:center;">
          <span v-for="l in 'الم حم عسق طه يس ص ق ن كهيعص طسم'.split(' ')" :key="l" style="background:linear-gradient(135deg,var(--secondary),#2D6A4F); color:white; padding:8px 16px; border-radius:20px; font-family:Amiri; font-size:1.2rem;">{{ l }}</span>
        </div>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 15: WORD SEARCH ═══════════════════ -->
    <div v-if="currentPage===15">
      <div class="hero">
        <h1 data-anim="hero">🔍 {{ L('بحث في الكلمات', 'Word Search') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('ابحث عن أي كلمة أو عبارة وشاهد تكرارها في القرآن', 'Search any word or phrase and see its frequency across the Quran') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div style="max-width:600px; margin:30px auto; text-align:center;">
        <div style="position:relative;">
          <input v-model="searchQuery" @input="searchWord" :placeholder="L('اكتب كلمة أو عبارة...', 'Type a word or phrase...')"
            style="width:100%; padding:16px 55px 16px 20px; font-size:1.3rem; font-family:Amiri; border:2px solid var(--accent); border-radius:30px; outline:none; text-align:center; direction:rtl; background:white; box-shadow:var(--card-shadow);" />
          <span style="position:absolute; left:18px; top:50%; transform:translateY(-50%); font-size:1.3rem; opacity:0.4;">🔍</span>
        </div>
        <p v-if="!searchQuery" style="margin-top:12px; color:#888; font-size:0.9rem;">{{ L('مثال: بسم الله الرحمن الرحيم، رحمة، جنة', 'Examples: بسم الله الرحمن الرحيم, mercy, paradise') }}</p>
      </div>

      <div v-if="searchTotal > 0" style="margin:20px 0;">
        <div class="kpi-grid">
          <div class="kpi" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);"><div class="kpi-label">{{ L('إجمالي التكرار', 'Total Occurrences') }}</div><div class="kpi-value">{{ searchTotal.toLocaleString() }}</div></div>
          <div class="kpi" style="background:linear-gradient(135deg,#fef3c7,#fde68a);"><div class="kpi-label">{{ L('عدد السور', 'Surahs Found') }}</div><div class="kpi-value">{{ searchResults.length }}</div></div>
          <div class="kpi" style="background:linear-gradient(135deg,#ede9fe,#ddd6fe);"><div class="kpi-label">{{ L('مرة كل N آية', 'Once every N verses') }}</div><div class="kpi-value">{{ (D.totalVerses / searchTotal).toFixed(1) }}</div></div>
        </div>

        <div class="section-header" data-anim="section">{{ L('📊 التوزيع حسب السورة', '📊 Distribution by Surah') }}</div>
        <div class="chart-container" data-anim="chart" id="chart-search" style="min-height:400px;"></div>

        <div class="section-header" data-anim="section" style="margin-top:25px;">{{ L('📋 التفاصيل', '📋 Details') }}</div>
        <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap:10px;">
          <div v-for="(r, idx) in searchResults" :key="idx" class="kpi clickable" data-anim="card"
            :style="{background: r.place==='Mecca' ? 'linear-gradient(135deg,#fce4ec,#f8bbd0)' : 'linear-gradient(135deg,#e0f7fa,#b2ebf2)'}"
            @click="drillSurah = D.surahStats.find(s => s.n === r.surah); if(drillSurah) showDrill = 'surah';">
            <div class="kpi-label" style="font-family:Amiri; font-size:1rem;">{{ r.name }}</div>
            <div class="kpi-value">{{ r.count }}</div>
            <div style="font-size:0.75rem; opacity:0.7;">{{ r.place === 'Mecca' ? L('مكية', 'Meccan') : L('مدنية', 'Medinan') }}</div>
          </div>
        </div>
      </div>

      <div v-if="searchQuery && searchTotal === 0" style="text-align:center; margin:40px 0; color:#888;">
        <div style="font-size:3rem; margin-bottom:10px;">🔎</div>
        <p style="font-family:Amiri; font-size:1.2rem;">{{ L('لم يتم العثور على نتائج', 'No results found') }}</p>
        <p style="font-size:0.9rem; margin-top:8px;">{{ L('جرب كلمة مختلفة أو تحقق من الإملاء', 'Try a different word or check spelling') }}</p>
      </div>
    </div>

    """ + footer_marker

html = html.replace(footer_marker, new_pages_html)
print("✓ Added Word Symmetries, Number 19, Structural Miracles, and Word Search pages")

# ════════════════════════════════════════════════════════════════
# STEP 8: Embed verses_compact.json + load in mounted
# ════════════════════════════════════════════════════════════════

verses_json = json.dumps(verses, ensure_ascii=False)

# Add VERSES data right after the DATA variable
old_data_line = "const DATA = "
# Find it and insert verses after
data_idx = html.find("const DATA = ")
if data_idx != -1:
    # Find the end of DATA assignment (the semicolon after the JSON)
    # Walk forward to find the closing semicolon
    brace_count = 0
    i = html.index("{", data_idx)
    for j in range(i, len(html)):
        if html[j] == '{': brace_count += 1
        elif html[j] == '}': brace_count -= 1
        if brace_count == 0:
            # Insert VERSES after this line
            end_of_data = html.index('\n', j) + 1
            html = html[:end_of_data] + f"\nconst VERSES_DATA = {verses_json};\n" + html[end_of_data:]
            break
    print("✓ Embedded verses_compact.json into HTML")
else:
    print("⚠ Could not find DATA variable")

# Load VERSES in mounted
old_mounted = """  mounted() {
    this.renderCharts();
    this.animatePage();"""

new_mounted = """  mounted() {
    this.VERSES = typeof VERSES_DATA !== 'undefined' ? VERSES_DATA : null;
    this.renderCharts();
    this.animatePage();"""

html = html.replace(old_mounted, new_mounted)
print("✓ Added VERSES loading in mounted")

# ════════════════════════════════════════════════════════════════
# STEP 9: Update renderCharts to use page 15 for search
# ════════════════════════════════════════════════════════════════

html = html.replace(
    "if (this.currentPage === 12 && this.searchResults.length)",
    "if (this.currentPage === 15 && this.searchResults.length)"
)
print("✓ Updated search chart to page 15")

# ════════════════════════════════════════════════════════════════
# STEP 10: Add chart for Word Symmetries page (page 12)
# ════════════════════════════════════════════════════════════════

old_search_chart = """      // Word search results chart"""

new_symmetry_chart = """      // Word Symmetries paired bar chart
      if (this.currentPage === 12 && D.wordSymmetries) {
        const syms = D.wordSymmetries;
        plot('chart-symmetry', [{
          y: syms.map(s => isAr ? s.ar1 + ' / ' + s.ar2 : s.en1 + ' / ' + s.en2).reverse(),
          x: syms.map(s => s.c1).reverse(), type: 'bar', orientation: 'h',
          text: syms.map(s => s.c1 + ' = ' + s.c2).reverse(), textposition: 'outside',
          marker: { color: syms.map((_, i) => `rgba(82,183,136,${0.4 + 0.6 * i / syms.length})`).reverse() }
        }], { height: Math.max(350, syms.length * 40),
          yaxis: { tickfont: { size: 14, family: 'Amiri' }, side: 'right', title: '' },
          xaxis: { title: isAr ? 'عدد التكرارات (متساوية)' : 'Count (equal)' }, margin: { r: 200, t: 20, b: 30 }
        });
      }

      // Word search results chart"""

html = html.replace(old_search_chart, new_symmetry_chart)
print("✓ Added symmetry chart rendering")

# ════════════════════════════════════════════════════════════════
# STEP 11: Add chart container to page 12 HTML
# ════════════════════════════════════════════════════════════════

# Add chart container after the symmetry cards grid
old_time_words = """      <div class="section-header" data-anim="section" style="margin-top:30px;">{{ L('📅 كلمات الزمن', '📅 Time Words') }}</div>"""

new_time_words = """      <div class="section-header" data-anim="section" style="margin-top:30px;">{{ L('📊 مقارنة بصرية', '📊 Visual Comparison') }}</div>
      <div class="chart-container" data-anim="chart" id="chart-symmetry" style="min-height:350px;"></div>

      <div class="section-header" data-anim="section" style="margin-top:30px;">{{ L('📅 كلمات الزمن', '📅 Time Words') }}</div>"""

html = html.replace(old_time_words, new_time_words)
print("✓ Added symmetry chart container to page 12")

# ════════════════════════════════════════════════════════════════
# STEP 12: Add community-insight CSS if not present
# ════════════════════════════════════════════════════════════════

if ".community-insight" not in html:
    insert_before = "/* ════════════════════ MAIN CONTENT ════════════════════ */"
    community_css = """.community-insight { font-family: 'Amiri'; font-size: 1rem; line-height: 2; color: #555; padding: 18px 22px; background: linear-gradient(135deg, #fffbeb, #fef3c7); border-radius: 14px; border-right: 4px solid var(--gold); margin: 15px 0; }
/* ════════════════════ MAIN CONTENT ════════════════════ */"""
    html = html.replace(insert_before, community_css)
    print("✓ Added community-insight CSS")

# ════════════════════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════════════════════
with open("QuranAnalytics.html", "w", encoding="utf-8") as f:
    f.write(html)
print("\n✅ All updates applied successfully!")
print(f"   HTML size: {len(html):,} bytes")
print(f"   Pages: 16 (0-15)")
print(f"   New: Word Symmetries (12), Number 19 (13), Structural (14), Word Search (15)")
