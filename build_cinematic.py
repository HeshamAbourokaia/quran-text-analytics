#!/usr/bin/env python3
"""Build the cinematic Quran Analytics HTML app."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "app_data.json"), encoding="utf-8") as f:
    data_json = json.dumps(json.load(f), ensure_ascii=False, separators=(',', ':'))

HTML = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>القرآن الكريم — تحليل نصي | Quran Text Analytics</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@300;400;600;700&family=Noto+Naskh+Arabic:wght@400;700&display=swap" rel="stylesheet">
<style>
/* ════════════════════ CSS VARIABLES ════════════════════ */
:root {
  --primary: #0D1B2A; --secondary: #1B4332; --accent: #52B788;
  --gold: #D4A574; --gold-glow: #E8C89E; --light: #D8F3DC;
  --bg: #FAFDF7; --bg-dark: #0D1B2A; --text: #1B4332;
  --mecca: #B7094C; --medina: #0091AD;
  --glass: rgba(255,255,255,0.08); --glass-border: rgba(255,255,255,0.15);
  --card-shadow: 0 8px 32px rgba(0,0,0,0.12);
  --glow: 0 0 30px rgba(82,183,136,0.3);
}
.dark { --bg: #0D1B2A; --text: #E0E0E0; --light: rgba(255,255,255,0.05); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Inter', 'Noto Naskh Arabic', 'Amiri', sans-serif;
  background: var(--bg); color: var(--text); direction: rtl;
  overflow-x: hidden;
}

/* ════════════════════ ISLAMIC GEOMETRIC PATTERN ════════════════════ */
.islamic-pattern {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 0; opacity: 0.03;
  background-image:
    repeating-conic-gradient(from 0deg at 50% 50%, transparent 0deg 60deg, rgba(82,183,136,0.3) 60deg 120deg, transparent 120deg 180deg);
  background-size: 120px 120px;
}

/* ════════════════════ PARTICLES CANVAS ════════════════════ */
#particles { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }

/* ════════════════════ LAYOUT ════════════════════ */
.app { display: flex; min-height: 100vh; position: relative; z-index: 1; }

/* ════════════════════ SIDEBAR ════════════════════ */
.sidebar {
  width: 280px; background: linear-gradient(180deg, #0D1B2A 0%, #1B4332 50%, #2D6A4F 100%);
  color: #D8F3DC; padding: 25px 15px; position: fixed; height: 100vh;
  overflow-y: auto; z-index: 100; border-left: 1px solid rgba(212,165,116,0.3);
  backdrop-filter: blur(20px);
}
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 4px; }
.sidebar-logo { text-align: center; padding: 15px 0; }
.sidebar-logo h1 { font-family: 'Amiri'; font-size: 1.6rem; color: var(--gold); text-shadow: 0 0 20px rgba(212,165,116,0.4); }
.sidebar-logo p { font-size: 0.8rem; color: #95D5B2; margin-top: 4px; }

/* Mode toggle */
.mode-toggle { display: flex; background: rgba(0,0,0,0.3); border-radius: 20px; padding: 3px; margin: 12px 0; }
.mode-btn { flex: 1; padding: 6px 8px; border-radius: 17px; border: none; cursor: pointer;
  font-size: 0.75rem; transition: all 0.3s; background: transparent; color: #95D5B2; }
.mode-btn.active { background: linear-gradient(135deg, var(--gold), #C68B59); color: #0D1B2A; font-weight: 600; }

/* Language toggle */
.lang-toggle { display: flex; gap: 5px; justify-content: center; margin: 10px 0; }
.lang-btn { padding: 5px 14px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2);
  background: transparent; color: #D8F3DC; cursor: pointer; font-size: 0.8rem; transition: all 0.3s; }
.lang-btn.active { background: var(--accent); color: #0D1B2A; border-color: var(--accent); }

.divider { border: none; border-top: 1px solid rgba(212,165,116,0.2); margin: 15px 0; }

/* Nav items */
.nav-item { padding: 10px 14px; border-radius: 10px; cursor: pointer; margin: 3px 0;
  font-family: 'Amiri'; font-size: 0.92rem; transition: all 0.3s; display: flex; align-items: center; gap: 8px; }
.nav-item:hover { background: rgba(82,183,136,0.15); transform: translateX(-3px); }
.nav-item.active { background: linear-gradient(90deg, rgba(212,165,116,0.25), transparent);
  border-right: 3px solid var(--gold); color: var(--gold); }
.nav-icon { font-size: 1.1rem; }
.sidebar-footer { text-align: center; font-size: 0.7rem; color: #52B788; margin-top: auto; padding-top: 20px; opacity: 0.7; }

/* ════════════════════ MAIN CONTENT ════════════════════ */
.main { flex: 1; margin-right: 280px; padding: 30px 45px; position: relative; }

/* ════════════════════ HERO SECTION ════════════════════ */
.hero { text-align: center; padding: 60px 20px 40px; position: relative; }
.hero-bismillah { font-family: 'Amiri'; font-size: 2.5rem; color: var(--gold);
  text-shadow: 0 0 30px rgba(212,165,116,0.3); margin-bottom: 10px; opacity: 0; }
.hero h1 { font-family: 'Amiri'; font-size: 3rem; color: var(--secondary);
  text-shadow: 0 2px 10px rgba(27,67,50,0.1); opacity: 0; }
.hero-sub { font-size: 1.1rem; color: #52B788; margin-top: 8px; opacity: 0; }
.hero-line { width: 120px; height: 3px; background: linear-gradient(90deg, transparent, var(--gold), transparent);
  margin: 20px auto; opacity: 0; }

/* ════════════════════ KPI FLYING CARDS ════════════════════ */
.kpi-grid { display: flex; gap: 15px; flex-wrap: wrap; margin: 25px 0; perspective: 1000px; }
.kpi {
  flex: 1; min-width: 150px; padding: 22px 16px; border-radius: 16px; text-align: center;
  position: relative; overflow: hidden; cursor: default;
  background: linear-gradient(135deg, #1B4332, #2D6A4F);
  box-shadow: var(--card-shadow); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  opacity: 0; transform: translateY(40px) rotateX(10deg);
}
.kpi:hover { transform: translateY(-8px) scale(1.03) !important; box-shadow: var(--glow), var(--card-shadow); }
.kpi::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle, rgba(212,165,116,0.1) 0%, transparent 60%);
  animation: shimmer 4s ease-in-out infinite; }
@keyframes shimmer { 0%,100% { opacity: 0.3; } 50% { opacity: 0.8; } }
.kpi-label { color: #B7E4C7; font-size: 0.8rem; margin-bottom: 6px; position: relative; }
.kpi-value { font-size: 2rem; font-weight: 700; color: white; position: relative;
  text-shadow: 0 0 15px rgba(255,255,255,0.2); }
.kpi-value .counter { display: inline-block; }

/* ════════════════════ SECTION HEADERS ════════════════════ */
.section-header {
  font-family: 'Amiri'; font-size: 1.5rem; font-weight: 700; color: var(--secondary);
  padding-bottom: 10px; margin: 35px 0 18px; text-align: right; position: relative;
  opacity: 0; transform: translateX(30px);
}
.section-header::after { content: ''; position: absolute; bottom: 0; right: 0;
  width: 80px; height: 3px; background: linear-gradient(90deg, var(--gold), transparent);
  border-radius: 3px; }

/* ════════════════════ INSIGHT BOX ════════════════════ */
.insight-box {
  background: linear-gradient(135deg, #f0f9f4, #d4eadc); border-right: 5px solid var(--accent);
  padding: 22px; border-radius: 0 14px 14px 0; margin: 18px 0; font-family: 'Amiri'; line-height: 2.2;
  text-align: right; direction: rtl; position: relative; overflow: hidden;
  box-shadow: 0 4px 15px rgba(82,183,136,0.1);
  opacity: 0; transform: translateX(20px);
}
.insight-box::before { content: ''; position: absolute; top: 0; right: 0; width: 4px; height: 100%;
  background: linear-gradient(180deg, var(--gold), var(--accent)); }

/* Community mode insight */
.community .insight-box {
  background: linear-gradient(135deg, #FFF8E1, #FFF3E0);
  border-right-color: var(--gold); font-size: 1.15rem;
}

/* ════════════════════ CHART CONTAINER ════════════════════ */
.chart-container { background: white; border-radius: 16px; padding: 18px; margin: 18px 0;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid rgba(82,183,136,0.1);
  opacity: 0; transform: translateY(20px); }

/* ════════════════════ VERSE CARD ════════════════════ */
.arabic-text {
  font-family: 'Amiri'; font-size: 1.35rem; direction: rtl; text-align: right; line-height: 2.4;
  color: var(--secondary); padding: 16px 20px; border-radius: 12px;
  background: linear-gradient(135deg, #f5faf5, #e8f5e8);
  border-right: 4px solid var(--gold); margin: 10px 0;
  box-shadow: inset 0 2px 8px rgba(82,183,136,0.05);
}

/* ════════════════════ WAW COMPARISON ════════════════════ */
.waw-compare { display: flex; gap: 20px; margin: 22px 0; }
.waw-card { flex: 1; border-radius: 16px; padding: 24px; text-align: center; direction: rtl;
  transition: all 0.3s; opacity: 0; transform: scale(0.9); }
.waw-card:hover { transform: scale(1.02) !important; }
.waw-hell { background: linear-gradient(135deg, #fce4ec, #ffcdd2); border: 2px solid var(--mecca); }
.waw-paradise { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border: 2px solid var(--accent); }

/* ════════════════════ DATA TABLE ════════════════════ */
.data-table { width: 100%; border-collapse: separate; border-spacing: 0; font-family: 'Amiri'; direction: rtl;
  border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.data-table th { padding: 12px 16px; background: linear-gradient(135deg, #1B4332, #2D6A4F);
  color: white; text-align: right; font-weight: 600; }
.data-table td { padding: 10px 16px; border-bottom: 1px solid #f0f7f0; text-align: right; }
.data-table tr:hover td { background: #f0f9f4; }
.highlight-row td { background: #e8f5e9 !important; }

/* ════════════════════ TABS ════════════════════ */
.tabs { display: flex; gap: 6px; overflow-x: auto; padding: 12px 0; margin-bottom: 22px; flex-wrap: nowrap; }
.tab { padding: 10px 18px; border-radius: 10px 10px 0 0; cursor: pointer; font-family: 'Amiri';
  font-size: 0.9rem; white-space: nowrap; border: 1px solid rgba(82,183,136,0.2);
  transition: all 0.3s; background: white; }
.tab:hover { background: var(--light); transform: translateY(-2px); }
.tab.active { background: linear-gradient(135deg, var(--secondary), #2D6A4F); color: white;
  border-color: var(--secondary); box-shadow: 0 4px 12px rgba(27,67,50,0.2); }

/* ════════════════════ ANTONYM PAIR CARDS ════════════════════ */
.pair-card { background: white; border: 1px solid rgba(82,183,136,0.15); border-radius: 14px;
  padding: 18px; margin: 12px 0; direction: rtl; transition: all 0.3s;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04); opacity: 0; transform: translateY(15px); }
.pair-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.08); transform: translateY(-3px) !important; }
.pair-row { display: flex; justify-content: space-around; align-items: center; margin-top: 14px; text-align: center; }
.pair-word { background: #f0f7f0; padding: 12px 22px; border-radius: 10px; }
.pair-word .word { font-family: 'Amiri'; font-size: 1.2rem; color: var(--secondary); }
.pair-word .count { font-size: 2rem; font-weight: 700; color: var(--secondary); margin-top: 4px; }
.pair-eq { font-size: 2rem; color: var(--gold); }
.pair-claimed { background: #f5f5f5; padding: 10px 16px; border-radius: 8px; }

/* ════════════════════ ABJAD CALCULATOR ════════════════════ */
.abjad-calc { background: linear-gradient(135deg, #FFF8E1, #FFF3E0); border: 2px solid var(--gold);
  border-radius: 16px; padding: 25px; margin: 20px 0; text-align: center; }
.abjad-input { font-family: 'Amiri'; font-size: 1.8rem; text-align: center; padding: 12px 20px;
  border: 2px solid var(--gold); border-radius: 12px; width: 80%; direction: rtl;
  background: white; outline: none; transition: all 0.3s; }
.abjad-input:focus { box-shadow: 0 0 20px rgba(212,165,116,0.3); border-color: var(--accent); }
.abjad-result { font-size: 3rem; font-weight: 700; color: var(--secondary); margin: 15px 0;
  text-shadow: 0 2px 10px rgba(27,67,50,0.1); }
.abjad-breakdown { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 15px 0; }
.abjad-letter { background: white; border: 1px solid var(--gold); border-radius: 10px;
  padding: 8px 14px; text-align: center; min-width: 50px; transition: all 0.3s; }
.abjad-letter:hover { transform: scale(1.1); background: var(--gold); color: white; }
.abjad-letter .ltr { font-family: 'Amiri'; font-size: 1.4rem; color: var(--secondary); }
.abjad-letter .val { font-size: 0.8rem; color: #888; }

/* ════════════════════ SCIENTIFIC REF CARD ════════════════════ */
.sci-card { background: white; border-radius: 14px; padding: 20px; margin: 14px 0;
  border: 1px solid rgba(82,183,136,0.1); box-shadow: 0 3px 12px rgba(0,0,0,0.04);
  transition: all 0.3s; direction: rtl; opacity: 0; transform: translateY(15px); }
.sci-card:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 25px rgba(0,0,0,0.08); }
.sci-badge { display: inline-block; background: linear-gradient(135deg, var(--secondary), #2D6A4F);
  color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; margin-bottom: 10px; }
.sci-ref { font-size: 0.85rem; color: #888; margin-top: 8px; }
.sci-science { background: #f0f9f4; padding: 12px; border-radius: 8px; margin-top: 10px;
  font-family: 'Amiri'; line-height: 1.8; border-right: 3px solid var(--accent); }

/* ════════════════════ INSIGHT CARDS (Data-Driven) ════════════════════ */
.insight-card { background: white; border: 1px solid rgba(82,183,136,0.1); border-radius: 14px;
  padding: 22px; margin: 14px 0; direction: rtl; text-align: right;
  box-shadow: 0 3px 15px rgba(27,67,50,0.06); transition: all 0.3s;
  opacity: 0; transform: translateY(15px); }
.insight-card:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 25px rgba(0,0,0,0.08); }
.insight-card .icon { font-size: 2.2rem; float: left; }
.insight-card .category { background: linear-gradient(135deg, #D8F3DC, #B7E4C7); color: var(--secondary);
  padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; float: right; font-weight: 600; }
.insight-card p { font-family: 'Amiri'; font-size: 1.1rem; line-height: 2.2; margin-top: 12px; clear: both; }

/* ════════════════════ COMMUNITY MODE ════════════════════ */
.community .section-header { font-size: 1.7rem; }
.community .kpi-value { font-size: 2.4rem; }
.community .arabic-text { font-size: 1.5rem; }

/* ════════════════════ NAV BUTTONS ════════════════════ */
.explore-grid { display: flex; gap: 12px; flex-wrap: wrap; }
.explore-btn { padding: 12px 22px; border-radius: 12px; border: 1px solid rgba(82,183,136,0.2);
  background: white; cursor: pointer; font-family: 'Amiri'; font-size: 0.95rem;
  transition: all 0.3s; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.explore-btn:hover { background: var(--accent); color: white; transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(82,183,136,0.3); }

/* ════════════════════ FOOTER ════════════════════ */
.footer { text-align: center; padding: 40px 20px; color: #52B788; font-size: 0.85rem;
  margin-top: 60px; border-top: 1px solid rgba(82,183,136,0.15); }

/* ════════════════════ RESPONSIVE ════════════════════ */
@media (max-width: 900px) {
  .sidebar { width: 220px; } .main { margin-right: 220px; padding: 20px; }
  .kpi-grid { flex-direction: column; } .waw-compare { flex-direction: column; }
  .hero h1 { font-size: 2rem; } .pair-row { flex-direction: column; gap: 10px; }
}
@media (max-width: 600px) {
  .sidebar { display: none; } .main { margin-right: 0; padding: 15px; }
}

/* ════════════════════ SCROLL ANIMATIONS ════════════════════ */
.reveal { opacity: 0; transform: translateY(30px); }
.reveal.active { opacity: 1; transform: translateY(0); transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
</style>
</head>
<body>
<div class="islamic-pattern"></div>
<canvas id="particles"></canvas>

<div id="app" :class="{ community: mode === 'community' }">
  <!-- ═══════════ SIDEBAR ═══════════ -->
  <div class="sidebar">
    <div class="sidebar-logo">
      <h1>﷽</h1>
      <h1>تحليل القرآن الكريم</h1>
      <p>Quran Text Analytics</p>
    </div>

    <div class="mode-toggle">
      <button class="mode-btn" :class="{active: mode==='academic'}" @click="mode='academic'">
        {{ L('أكاديمي', 'Academic') }}
      </button>
      <button class="mode-btn" :class="{active: mode==='community'}" @click="mode='community'">
        {{ L('مجتمعي', 'Community') }}
      </button>
    </div>

    <div class="lang-toggle">
      <button class="lang-btn" :class="{active: lang==='ar'}" @click="lang='ar'">عربي</button>
      <button class="lang-btn" :class="{active: lang==='en'}" @click="lang='en'">English</button>
    </div>

    <hr class="divider">

    <div v-for="(page, idx) in pages" :key="idx"
         class="nav-item" :class="{active: currentPage===idx}"
         @click="goTo(idx)">
      <span class="nav-icon">{{ page.icon }}</span>
      {{ lang === 'ar' ? page.ar : page.en }}
    </div>

    <hr class="divider">
    <div class="sidebar-footer">
      Master of Business Analytics<br>NLP & Text Analytics Project<br><br>
      Data: semarketir/quranjson<br>
      {{ D.totalVerses.toLocaleString() }} verses · 114 surahs
    </div>
  </div>

  <!-- ═══════════ MAIN CONTENT ═══════════ -->
  <div class="main">

    <!-- ═══════════════════ PAGE 0: OVERVIEW ═══════════════════ -->
    <div v-if="currentPage===0">
      <div class="hero">
        <div class="hero-bismillah" data-anim="hero">بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ</div>
        <h1 data-anim="hero">{{ L('القرآن الكريم — تحليل نصي', 'Quran Text Analytics') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('لوحة تحليل نصي متقدمة بالذكاء الاصطناعي', 'Advanced NLP & Text Analytics Dashboard') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div class="kpi-grid">
        <div class="kpi" v-for="(k,i) in overviewKPIs" :key="i">
          <div class="kpi-label">{{ L(k.ar, k.en) }}</div>
          <div class="kpi-value">{{ k.val }}</div>
        </div>
      </div>

      <div class="section-header" data-anim="section">{{ L('📊 عدد الآيات لكل سورة', '📊 Verse Count by Surah') }}</div>
      <div class="chart-container" data-anim="chart" id="chart-surah-bars"></div>

      <div class="insight-box" data-anim="insight">
        <strong>{{ L('💡 نتيجة رئيسية:', '💡 Key Finding:') }}</strong><br>
        <template v-if="mode==='community'">
          {{ L(
            'تخيّلي أن القرآن كتاب من جزأين: الجزء المكي (' + D.meccanSurahs + ' سورة) قصير وقوي — مثل العناوين العريضة في الصحيفة. الجزء المدني (' + D.medinanSurahs + ' سورة) أطول وأكثر تفصيلاً — مثل المقالات الكاملة. الأول يُلهب القلب بالإيمان، والثاني ينظّم حياة المسلمين.',
            'Imagine the Quran as a two-part book: The Meccan part (' + D.meccanSurahs + ' surahs) is short and powerful — like bold headlines. The Medinan part (' + D.medinanSurahs + ' surahs) is longer and detailed — like full articles. The first ignites faith, the second organizes daily life.'
          ) }}
        </template>
        <template v-else>
          {{ L(
            'السور المكية (' + D.meccanSurahs + ' سورة) أقصر في المتوسط وتركز على العقيدة. السور المدنية (' + D.medinanSurahs + ' سورة) أطول وتتناول التشريعات.',
            'Meccan surahs (' + D.meccanSurahs + ') are shorter, focusing on faith. Medinan surahs (' + D.medinanSurahs + ') are longer, covering legislation.'
          ) }}
        </template>
      </div>

      <div class="section-header" data-anim="section">{{ L('🚀 استكشف الأقسام', '🚀 Explore Sections') }}</div>
      <div class="explore-grid">
        <button v-for="(p,i) in pages.slice(1)" :key="i" class="explore-btn" @click="goTo(i+1)">
          {{ p.icon }} {{ lang === 'ar' ? p.ar : p.en }}
        </button>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 1: WORD ANALYSIS ═══════════════════ -->
    <div v-if="currentPage===1">
      <div class="hero">
        <h1 data-anim="hero">📝 {{ L('تحليل الكلمات', 'Word Analysis') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('تكرار الكلمات العربية والمصطلحات الأكثر شيوعاً', 'Arabic word frequency and most common terms') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div class="section-header" data-anim="section">{{ L('🏆 أكثر 30 كلمة تكراراً', '🏆 Top 30 Most Frequent Words') }}</div>
      <div class="chart-container" data-anim="chart" id="chart-word-freq"></div>

      <div class="insight-box" data-anim="insight" v-if="mode==='community'">
        <strong>{{ L('💡 ماذا يعني هذا؟', '💡 What does this mean?') }}</strong><br>
        {{ L(
          'الكلمة الأكثر تكراراً هي "' + D.topWords[0].w + '" — تظهر ' + D.topWords[0].c.toLocaleString() + ' مرة! تخيّل أنك تقرأ كتاباً وكل بضع جمل تجد نفس الكلمة — هذا يعني أن الموضوع المركزي واضح جداً. القرآن يركز على الله والإيمان والهداية أكثر من أي شيء آخر.',
          'The most repeated word is "' + D.topWords[0].w + '" — appearing ' + D.topWords[0].c.toLocaleString() + ' times! Imagine reading a book where every few sentences you see the same word — that means the central theme is crystal clear.'
        ) }}
      </div>

      <div class="section-header" data-anim="section">{{ L('📋 جدول الكلمات', '📋 Word Table') }}</div>
      <table class="data-table">
        <tr><th>#</th><th>{{ L('الكلمة', 'Word') }}</th><th>{{ L('التكرار', 'Count') }}</th></tr>
        <tr v-for="(w,i) in D.topWords.slice(0, 20)" :key="i">
          <td>{{ i+1 }}</td>
          <td style="font-family:Amiri; font-size:1.2rem;">{{ w.w }}</td>
          <td>{{ w.c.toLocaleString() }}</td>
        </tr>
      </table>
    </div>

    <!-- ═══════════════════ PAGE 2: MECCA VS MEDINA ═══════════════════ -->
    <div v-if="currentPage===2">
      <div class="hero">
        <h1 data-anim="hero">🗺️ {{ L('مكة والمدينة', 'Mecca vs Medina') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('مقارنة فترات النزول من خلال التحليل النصي', 'Comparing revelation periods through text analytics') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>
      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-label">{{ L('سور مكية', 'Meccan') }}</div><div class="kpi-value">{{ D.meccanSurahs }}</div></div>
        <div class="kpi"><div class="kpi-label">{{ L('سور مدنية', 'Medinan') }}</div><div class="kpi-value">{{ D.medinanSurahs }}</div></div>
        <div class="kpi"><div class="kpi-label">{{ L('متوسط المكية', 'Meccan Avg') }}</div><div class="kpi-value">{{ D.meccanAvgWc }}</div></div>
        <div class="kpi"><div class="kpi-label">{{ L('متوسط المدنية', 'Medinan Avg') }}</div><div class="kpi-value">{{ D.medinanAvgWc }}</div></div>
      </div>
      <div class="section-header" data-anim="section">{{ L('💬 المشاعر حسب السورة', '💬 Sentiment by Surah') }}</div>
      <div class="chart-container" data-anim="chart" id="chart-sentiment"></div>
      <div class="insight-box" data-anim="insight">
        <template v-if="mode==='community'">
          {{ L(
            'الآيات المدنية أطول بمعدل ' + (D.medinanAvgWc / D.meccanAvgWc).toFixed(1) + ' مرة! السبب بسيط: في مكة كانت الرسالة "آمنوا بالله" — رسائل قصيرة وقوية. في المدينة أصبحت الرسالة "كيف تعيشون كمسلمين" — قوانين وتفاصيل تحتاج شرحاً أطول.',
            'Medinan verses are ' + (D.medinanAvgWc / D.meccanAvgWc).toFixed(1) + 'x longer! The reason is simple: In Mecca the message was "Believe in God" — short powerful proclamations. In Medina it became "How to live as Muslims" — laws and details needing longer explanations.'
          ) }}
        </template>
        <template v-else>
          {{ L(
            'الآيات المدنية أطول بمعدل ' + (D.medinanAvgWc / D.meccanAvgWc).toFixed(1) + 'x من المكية. يعكس التحول من الإعلانات القصيرة إلى التوجيهات التفصيلية.',
            'Medinan verses are ' + (D.medinanAvgWc / D.meccanAvgWc).toFixed(1) + 'x longer than Meccan, reflecting the shift from proclamations to detailed guidance.'
          ) }}
        </template>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 3: EMOTIONAL PROFILING ═══════════════════ -->
    <div v-if="currentPage===3">
      <div class="hero">
        <h1 data-anim="hero">🎭 {{ L('البصمة العاطفية', 'Emotional Profiling') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('ماذا تقول البيانات عن النبرة العاطفية للقرآن؟', 'What does the data say about the Qurans emotional tone?') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>
      <div class="kpi-grid">
        <div class="kpi" style="background:linear-gradient(135deg,#52B788,#2D6A4F)"><div class="kpi-label">{{ L('رحمة', 'Mercy') }}</div><div class="kpi-value">{{ totalSentiment('mercy').toLocaleString() }}</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#B7094C,#880E4F)"><div class="kpi-label">{{ L('تحذير', 'Warning') }}</div><div class="kpi-value">{{ totalSentiment('warning').toLocaleString() }}</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#D4A574,#C68B59)"><div class="kpi-label">{{ L('هداية', 'Guidance') }}</div><div class="kpi-value">{{ totalSentiment('guidance').toLocaleString() }}</div></div>
        <div class="kpi" style="background:linear-gradient(135deg,#0091AD,#006B7F)"><div class="kpi-label">{{ L('أمل', 'Hope') }}</div><div class="kpi-value">{{ totalSentiment('hope').toLocaleString() }}</div></div>
      </div>
      <div class="section-header" data-anim="section">{{ L('📊 توزيع المشاعر', '📊 Sentiment Distribution') }}</div>
      <div class="chart-container" data-anim="chart" id="chart-sentiment-pie"></div>
      <div class="insight-box" data-anim="insight">
        <template v-if="mode==='community'">
          {{ L(
            'هل تعلمين أن لغة الرحمة والهداية تشكلان معاً أكثر من 60% من النبرة العاطفية في القرآن؟ هذا يعني أنه لو كان القرآن شخصاً يتحدث إليكِ، فأغلب كلامه سيكون "أنا أرحمكِ وأرشدكِ" — وليس "أنا أخوّفكِ". الرحمة هي اللغة السائدة.',
            'Did you know that mercy and guidance language together make up over 60% of the Qurans emotional tone? If the Quran were a person speaking to you, most of their words would be "I have mercy on you and guide you" — not "I frighten you". Compassion is the dominant language.'
          ) }}
        </template>
        <template v-else>
          {{ L(
            'لغة الرحمة والهداية تشكلان أكثر من 60% من النبرة العاطفية. النبرة الغالبة هي الإرشاد والرحمة.',
            'Mercy and Guidance language make up over 60% of the emotional tone. The dominant tone is compassion and guidance.'
          ) }}
        </template>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 4: WAW MIRACLE ═══════════════════ -->
    <div v-if="currentPage===4">
      <div class="hero">
        <h1 data-anim="hero">🌟 {{ L('معجزة الواو', 'The Waw Miracle') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('الواو لا تُذكر إلا بعد السابعة', 'The Waw is only mentioned after the 7th') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div class="insight-box" data-anim="insight" style="border-right:5px solid var(--gold); background:linear-gradient(135deg,#FFF8E1,#FFF3E0);">
        <strong>{{ L('🔑 القاعدة:', '🔑 The Rule:') }}</strong><br><br>
        <template v-if="mode==='community'">
          {{ L(
            'في العربية عند عدّ الأشياء: واحد، اثنان، ثلاثة... سبعة وَثمانية. الواو (وَ = and) لا تأتي إلا بعد السابع! القرآن يطبق هذه القاعدة بدقة مذهلة في عدة مواضع:',
            'In Arabic counting: one, two, three... seven AND eight. The Waw (وَ = and) only appears after the 7th! The Quran applies this rule with stunning precision:'
          ) }}
        </template>
        <template v-else>
          {{ L(
            'في اللغة العربية: الواو لا تُذكر إلا بعد السابعة. القرآن يطبق هذه القاعدة بدقة.',
            'In Arabic: the Waw (and) appears only after the 7th item. The Quran applies this rule precisely.'
          ) }}
        </template>
      </div>

      <div class="section-header" data-anim="section">{{ L('🔥 أبواب النار والجنة', '🔥 Gates of Hell vs Paradise') }}</div>
      <div class="waw-compare">
        <div class="waw-card waw-hell" data-anim="waw">
          <h3 style="color:var(--mecca);">🔥 {{ L('أبواب النار = 7', 'Gates of Hell = 7') }}</h3>
          <p style="color:var(--mecca); font-weight:bold; font-size:1.2rem;">{{ L('بدون واو ❌', 'NO Waw ❌') }}</p>
          <p style="color:#888; font-size:0.85rem; margin:8px 0;">39:71</p>
          <div v-if="D.wawVerses.hell" class="arabic-text" style="font-size:1.1rem;">{{ D.wawVerses.hell.a }}</div>
          <div style="background:#ffebee; padding:12px; border-radius:8px; margin-top:12px; font-family:Amiri; font-size:1.1rem; color:var(--mecca);">
            {{ L('حتى إذا جاؤوها فُتحت أبوابها', 'Until they reach it, its gates are opened') }}
            <br><span style="font-size:0.85rem; color:#888;">{{ L('← لا يوجد واو قبل "فُتحت"', '← No Waw before "opened"') }}</span>
          </div>
        </div>
        <div class="waw-card waw-paradise" data-anim="waw">
          <h3 style="color:var(--secondary);">🌴 {{ L('أبواب الجنة = 8', 'Gates of Paradise = 8') }}</h3>
          <p style="color:var(--secondary); font-weight:bold; font-size:1.2rem;">{{ L('مع واو ✅', 'WITH Waw ✅') }}</p>
          <p style="color:#888; font-size:0.85rem; margin:8px 0;">39:73</p>
          <div v-if="D.wawVerses.paradise" class="arabic-text" style="font-size:1.1rem;">{{ D.wawVerses.paradise.a }}</div>
          <div style="background:#e8f5e9; padding:12px; border-radius:8px; margin-top:12px; font-family:Amiri; font-size:1.1rem; color:var(--secondary);">
            {{ L('حتى إذا جاؤوها وَفُتحت أبوابها', 'Until they reach it AND its gates are opened') }}
            <br><span style="font-size:0.85rem; color:#888;">{{ L('← الواو موجودة = بعد السابعة', '← Waw present = after 7th gate') }}</span>
          </div>
        </div>
      </div>

      <div class="section-header" data-anim="section">{{ L('🕌 أصحاب الكهف (18:22)', '🕌 People of the Cave (18:22)') }}</div>
      <div v-if="D.wawVerses.cave" class="arabic-text" style="margin-bottom:16px;">{{ D.wawVerses.cave.a }}</div>
      <table class="data-table" style="max-width:600px; margin:0 auto;">
        <tr><th>{{ L('العدد', 'Count') }}</th><th>{{ L('النص', 'Text') }}</th><th>{{ L('واو؟', 'Waw?') }}</th></tr>
        <tr><td>3</td><td style="font-family:Amiri;">ثلاثة <strong>رابعهم</strong></td><td style="color:var(--mecca);">❌</td></tr>
        <tr><td>5</td><td style="font-family:Amiri;">خمسة <strong>سادسهم</strong></td><td style="color:var(--mecca);">❌</td></tr>
        <tr class="highlight-row"><td><strong>7</strong></td><td style="font-family:Amiri;">سبعة <strong style="color:var(--gold); font-size:1.4rem;">وَ</strong><strong>ثامنهم</strong></td><td style="color:var(--secondary); font-size:1.3rem;">✅</td></tr>
      </table>

      <div class="section-header" data-anim="section">{{ L('☁️ صفات الله (39:6)', '☁️ Divine Attributes (39:6)') }}</div>
      <div v-if="D.wawVerses.attributes" class="arabic-text">{{ D.wawVerses.attributes.a }}</div>
    </div>

    <!-- ═══════════════════ PAGE 5: LETTER FREQUENCY ═══════════════════ -->
    <div v-if="currentPage===5">
      <div class="hero">
        <h1 data-anim="hero">🔤 {{ L('تحليل الحروف', 'Letter Frequency') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('توزيع الحروف العربية في القرآن الكريم', 'Distribution of Arabic letters across the entire Quran') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>
      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-label">{{ L('إجمالي الحروف', 'Total Letters') }}</div><div class="kpi-value">{{ D.totalLetters.toLocaleString() }}</div></div>
        <div class="kpi"><div class="kpi-label">{{ L('حرف الواو', 'Waw Count') }}</div><div class="kpi-value">{{ D.wawCount.toLocaleString() }}</div></div>
      </div>
      <div class="section-header" data-anim="section">{{ L('📊 تكرار الحروف', '📊 Letter Frequencies') }}</div>
      <div class="chart-container" data-anim="chart" id="chart-letters"></div>
    </div>

    <!-- ═══════════════════ PAGE 6: DIVINE PRONOUNS ═══════════════════ -->
    <div v-if="currentPage===6">
      <div class="hero">
        <h1 data-anim="hero">👑 {{ L('ضمائر الذات الإلهية', 'Divine Pronouns') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('كيف يتحدث الله عن نفسه في القرآن', 'How God refers to Himself in the Quran') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>
      <div class="chart-container" data-anim="chart" id="chart-pronouns"></div>
      <div class="insight-box" data-anim="insight">
        <template v-if="mode==='community'">
          {{ L(
            'هل لاحظتِ أن الله يستخدم "نحن" أكثر من "أنا"؟ في العربية هذا يُسمى "نون العظمة" — ليس لأن الله أكثر من واحد، بل لأن العظمة في العربية تُعبّر عنها بصيغة الجمع. مثل الملك الذي يقول "نحن نأمر" بدلاً من "أنا آمر".',
            'Notice God uses "We" more than "I"? In Arabic this is the "Royal We" (Nūn al-Aẓamah) — not because God is plural, but because greatness in Arabic uses plural form. Like a king saying "We decree" instead of "I decree".'
          ) }}
        </template>
        <template v-else>
          {{ L(
            'استخدام ضمير "نحن" (نون العظمة) يفوق ضمير "أنا" — يعكس الجلال والعظمة الإلهية في الأسلوب القرآني.',
            'The majestic "We" pronoun usage exceeds singular "I" — reflecting divine majesty in Quranic style.'
          ) }}
        </template>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 7: ANTONYM PAIRS ═══════════════════ -->
    <div v-if="currentPage===7">
      <div class="hero">
        <h1 data-anim="hero">⚖️ {{ L('التوازن في الأزواج', 'Antonym Pair Balance') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('هل تتكرر الكلمات المتضادة بنفس العدد؟', 'Do antonym words appear the same number of times?') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>
      <div class="insight-box" data-anim="insight" style="background:linear-gradient(135deg,#FFF8E1,#FFF3E0); border-right-color:var(--gold);">
        <template v-if="mode==='community'">
          {{ L(
            'يُقال إن القرآن يكرر الكلمات المتضادة بنفس العدد — مثل "حياة" و"موت" تظهران نفس عدد المرات! هذا ادعاء شائع على الإنترنت. هنا نتحقق منه بالبيانات الفعلية. النتائج تعتمد على طريقة العدّ: هل نعد الكلمة الأصلية فقط أم كل مشتقاتها؟',
            'It is claimed that the Quran repeats antonym words the same number of times — like "life" and "death" appearing equally! This is a popular internet claim. Here we verify it with actual data. Results depend on counting methodology.'
          ) }}
        </template>
        <template v-else>
          {{ L('التحقق من ادعاءات التوازن العددي بين الأزواج المتضادة في القرآن.', 'Verifying numerical balance claims between antonym pairs in the Quran.') }}
        </template>
      </div>

      <div v-for="(pr, idx) in D.antonymPairs" :key="idx" class="pair-card" data-anim="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="font-family:Amiri; font-size:1.2rem; color:var(--secondary);">
            {{ pr.match ? '✅' : (pr.diff <= 3 ? '🟡' : '❌') }}
            {{ L(pr.label_ar, pr.label_en) }}
          </strong>
          <span :style="{color: pr.match ? 'var(--accent)' : (pr.diff<=3 ? 'var(--gold)' : 'var(--mecca)'), fontWeight:'bold'}">
            {{ pr.match ? L('متطابق!', 'MATCH!') : (pr.diff <= 3 ? L('قريب جداً', 'Very close') : L('غير متطابق', 'No match')) }}
          </span>
        </div>
        <div class="pair-row">
          <div class="pair-word"><div class="word">"{{ pr.ar_a }}"</div><div class="count">{{ pr.found_a }}</div><div style="font-size:0.8rem; color:#888;">{{ L('آية', 'verses') }}</div></div>
          <div class="pair-eq">{{ pr.match ? '=' : '≈' }}</div>
          <div class="pair-word"><div class="word">"{{ pr.ar_b }}"</div><div class="count">{{ pr.found_b }}</div><div style="font-size:0.8rem; color:#888;">{{ L('آية', 'verses') }}</div></div>
          <div class="pair-claimed"><div style="font-size:0.8rem; color:#888;">{{ L('المُدّعى', 'Claimed') }}</div><div style="font-size:1.2rem; font-weight:bold; color:#888;">{{ pr.claimed }}</div></div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 8: CALENDAR CLAIMS ═══════════════════ -->
    <div v-if="currentPage===8">
      <div class="hero">
        <h1 data-anim="hero">📅 {{ L('ادعاءات الكلمات التقويمية', 'Calendar Word Claims') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('هل كلمة "يوم" تظهر 365 مرة؟', 'Does the word "day" appear 365 times?') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div v-for="(cr, idx) in D.calendarClaims" :key="idx" class="pair-card" data-anim="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="font-family:Amiri; font-size:1.3rem;">
            {{ (cr.verse_match || cr.total_match) ? '✅' : '🔍' }} {{ L(cr.label_ar, cr.label_en) }}
          </strong>
        </div>
        <p style="font-family:Amiri; margin:10px 0; color:#666;">{{ L(cr.note_ar, cr.note_en) }}</p>
        <div class="pair-row">
          <div class="pair-word"><div style="font-size:0.8rem; color:#888;">{{ L('آيات تحتوي الكلمة', 'Verses containing') }}</div><div class="count">{{ cr.verse_count }}</div></div>
          <div class="pair-word"><div style="font-size:0.8rem; color:#888;">{{ L('إجمالي التكرار', 'Total occurrences') }}</div><div class="count">{{ cr.total_count }}</div></div>
          <div class="pair-claimed"><div style="font-size:0.8rem; color:#888;">{{ L('المُدّعى', 'Claimed') }}</div><div class="count" style="color:#888;">{{ cr.claimed }}</div></div>
        </div>
        <div class="insight-box" data-anim="insight" style="margin-top:15px;">
          {{ L(
            'النتائج تعتمد على المنهجية: هل نعد الكلمة بصيغتها الأصلية فقط، أم كل المشتقات، أم عدد الآيات التي تحتويها؟ كل طريقة تعطي أرقاماً مختلفة.',
            'Results depend on methodology: do we count the exact word only, all derivatives, or verses containing it? Each method yields different numbers.'
          ) }}
        </div>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 9: ABJAD CALCULATOR ═══════════════════ -->
    <div v-if="currentPage===9">
      <div class="hero">
        <h1 data-anim="hero">🔢 {{ L('حساب الجُمَّل', 'Abjad Numerals') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('كل حرف عربي له قيمة عددية', 'Every Arabic letter has a numerical value') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div class="insight-box" data-anim="insight" style="background:linear-gradient(135deg,#FFF8E1,#FFF3E0); border-right-color:var(--gold);">
        <template v-if="mode==='community'">
          {{ L(
            'حساب الجُمَّل نظام عربي قديم حيث كل حرف من الأبجدية العربية له قيمة عددية. مثلاً: ا=1، ب=2، ج=3... وهكذا حتى غ=1000. يمكنك حساب القيمة العددية لأي كلمة بجمع قيم حروفها!',
            'Abjad numerals is an ancient Arabic system where each letter has a number. For example: ا=1, ب=2, ج=3... up to غ=1000. You can calculate any words numerical value by summing its letters!'
          ) }}
        </template>
        <template v-else>
          {{ L('نظام حساب الجُمَّل (Abjad) يربط كل حرف عربي بقيمة عددية.', 'The Abjad system assigns a numerical value to each Arabic letter.') }}
        </template>
      </div>

      <!-- Calculator -->
      <div class="abjad-calc" data-anim="card">
        <h3 style="font-family:Amiri; margin-bottom:15px;">{{ L('🧮 احسب قيمة أي كلمة', '🧮 Calculate Any Word') }}</h3>
        <input class="abjad-input" v-model="abjadInput" :placeholder="L('اكتب كلمة عربية...', 'Type an Arabic word...')" @input="calcAbjad">
        <div class="abjad-result">{{ abjadTotal }}</div>
        <div class="abjad-breakdown" v-if="abjadLetters.length">
          <div v-for="(a,i) in abjadLetters" :key="i" class="abjad-letter">
            <div class="ltr">{{ a.l }}</div>
            <div class="val">{{ a.v }}</div>
          </div>
        </div>
      </div>

      <!-- Abjad reference table -->
      <div class="section-header" data-anim="section">{{ L('📋 جدول الحروف والقيم', '📋 Letter Values Table') }}</div>
      <table class="data-table" style="max-width:700px; margin:0 auto;">
        <tr><th>{{ L('الحرف', 'Letter') }}</th><th>{{ L('القيمة', 'Value') }}</th><th>{{ L('الحرف', 'Letter') }}</th><th>{{ L('القيمة', 'Value') }}</th></tr>
        <tr v-for="i in Math.ceil(D.abjadTable.length/2)" :key="i">
          <td style="font-family:Amiri; font-size:1.4rem;">{{ D.abjadTable[(i-1)*2]?.l }}</td>
          <td>{{ D.abjadTable[(i-1)*2]?.v }}</td>
          <td style="font-family:Amiri; font-size:1.4rem;">{{ D.abjadTable[(i-1)*2+1]?.l || '' }}</td>
          <td>{{ D.abjadTable[(i-1)*2+1]?.v || '' }}</td>
        </tr>
      </table>

      <!-- Iron miracle -->
      <div class="section-header" data-anim="section">{{ L('⚗️ معجزة الحديد', '⚗️ The Iron Miracle') }}</div>
      <div v-for="(ex, idx) in D.abjadExamples" :key="idx" class="pair-card" data-anim="card" style="text-align:center;">
        <h3 style="font-family:Amiri; font-size:1.5rem; color:var(--secondary);">{{ L(ex.word_ar, ex.word_en) }}</h3>
        <div style="font-size:3rem; font-weight:700; color:var(--gold); margin:10px 0;">{{ ex.value }}</div>
        <div v-if="ex.letters.length" class="abjad-breakdown">
          <div v-for="(a,i) in ex.letters" :key="i" class="abjad-letter">
            <div class="ltr">{{ a.l }}</div>
            <div class="val">{{ a.v }}</div>
          </div>
        </div>
        <p style="font-family:Amiri; font-size:1.1rem; margin-top:15px; line-height:2;">
          {{ L(ex.significance_ar, ex.significance_en) }}
        </p>
        <div :style="{background: ex.verified ? '#e8f5e9' : '#fff3e0', padding:'12px', borderRadius:'10px', marginTop:'12px', fontFamily:'Amiri'}">
          <strong>{{ ex.verified ? '✅' : '🔍' }}</strong> {{ L(ex.note_ar, ex.note_en) }}
        </div>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 10: SCIENTIFIC REFERENCES ═══════════════════ -->
    <div v-if="currentPage===10">
      <div class="hero">
        <h1 data-anim="hero">🔬 {{ L('الإشارات العلمية', 'Scientific References') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('آيات تتوافق مع اكتشافات علمية حديثة', 'Verses aligning with modern scientific discoveries') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-label">{{ L('إجمالي الإشارات', 'Total References') }}</div><div class="kpi-value">{{ D.scientificRefs.length }}</div></div>
        <div class="kpi"><div class="kpi-label">{{ L('المجالات العلمية', 'Scientific Fields') }}</div><div class="kpi-value">{{ D.sciCategories.length }}</div></div>
      </div>

      <div class="insight-box" data-anim="insight">
        <template v-if="mode==='community'">
          {{ L(
            'هذه الصفحة تعرض آيات قرآنية تتوافق مع اكتشافات علمية لم تكن معروفة قبل 1400 سنة. نعرض الآية والحقيقة العلمية — الهدف ليس إثبات أو نفي بل عرض البيانات وترك الاستنتاج لكِ.',
            'This page shows Quranic verses that align with scientific discoveries unknown 1400 years ago. We present the verse and the scientific fact — the goal is to present data and let you draw conclusions.'
          ) }}
        </template>
        <template v-else>
          {{ L('عرض بيانات الآيات المتوافقة مع الاكتشافات العلمية الحديثة.', 'Data presentation of verses aligning with modern scientific discoveries.') }}
        </template>
      </div>

      <div class="section-header" data-anim="section">{{ L('📊 التوزيع حسب المجال', '📊 Distribution by Field') }}</div>
      <div class="chart-container" data-anim="chart" id="chart-sci-cats"></div>

      <!-- Tabs by category -->
      <div class="tabs">
        <div class="tab" :class="{active: sciFilter==='all'}" @click="sciFilter='all'">{{ L('الكل', 'All') }}</div>
        <div v-for="cat in D.sciCategories" :key="cat.cat" class="tab"
             :class="{active: sciFilter===cat.cat}" @click="sciFilter=cat.cat">
          {{ lang==='ar' ? (D.scientificRefs.find(r=>r.cat_en===cat.cat)||{}).cat_ar||cat.cat : cat.cat }}
        </div>
      </div>

      <div v-for="(ref, idx) in filteredSciRefs" :key="idx" class="sci-card" data-anim="card">
        <span class="sci-badge">{{ L(ref.cat_ar, ref.cat_en) }}</span>
        <h3 style="font-family:Amiri; font-size:1.2rem; margin:8px 0;">{{ L(ref.t_ar, ref.t_en) }}</h3>
        <div class="sci-ref">{{ L('سورة', 'Surah') }} {{ ref.s }}:{{ ref.v }}</div>
        <div v-if="ref.ar_text" class="arabic-text" style="font-size:1.1rem; margin:10px 0;">{{ ref.ar_text }}</div>
        <div v-if="ref.en_text" style="background:#f8f8f8; padding:10px; border-radius:8px; font-style:italic; color:#666; margin:8px 0;">{{ ref.en_text }}</div>
        <div class="sci-science">
          <strong>{{ L('🔬 الحقيقة العلمية:', '🔬 Scientific Fact:') }}</strong><br>
          {{ L(ref.sc_ar, ref.sc_en) }}
        </div>
      </div>
    </div>

    <!-- ═══════════════════ PAGE 11: DATA-DRIVEN INSIGHTS ═══════════════════ -->
    <div v-if="currentPage===11">
      <div class="hero">
        <h1 data-anim="hero">💡 {{ L('استنتاجات البيانات', 'Data-Driven Insights') }}</h1>
        <p class="hero-sub" data-anim="hero">{{ L('ماذا تكشف الأرقام؟', 'What do the numbers reveal?') }}</p>
        <div class="hero-line" data-anim="hero"></div>
      </div>

      <div v-for="(ins, idx) in insights" :key="idx" class="insight-card" data-anim="card">
        <span class="icon">{{ ins.icon }}</span>
        <span class="category">{{ L(ins.cat_ar, ins.cat_en) }}</span>
        <p>{{ L(ins.ar, ins.en) }}</p>
      </div>
    </div>

    <!-- ════════════ FOOTER ════════════ -->
    <div class="footer">
      <p style="font-family:Amiri; font-size:1rem; margin-bottom:8px;">{{ L('سُبْحَانَ رَبِّكَ رَبِّ الْعِزَّةِ عَمَّا يَصِفُونَ', 'Glory be to your Lord, the Lord of Might, above what they describe') }}</p>
      <p>Master of Business Analytics — NLP & Text Analytics Project</p>
      <p>Data: semarketir/quranjson · Built with Vue.js 3 + GSAP + Plotly.js</p>
    </div>
  </div>
</div>

<script>
const DATA = ''' + data_json + r''';

const { createApp } = Vue;

createApp({
  data() {
    return {
      currentPage: 0,
      lang: 'ar',
      mode: 'community',
      D: DATA,
      sciFilter: 'all',
      abjadInput: '',
      abjadTotal: 0,
      abjadLetters: [],
      pages: [
        { icon: '📖', ar: 'نظرة عامة', en: 'Overview' },
        { icon: '📝', ar: 'تحليل الكلمات', en: 'Word Analysis' },
        { icon: '🗺️', ar: 'مكة والمدينة', en: 'Mecca vs Medina' },
        { icon: '🎭', ar: 'البصمة العاطفية', en: 'Emotional Profiling' },
        { icon: '🌟', ar: 'معجزة الواو', en: 'Waw Miracle' },
        { icon: '🔤', ar: 'تحليل الحروف', en: 'Letter Frequency' },
        { icon: '👑', ar: 'ضمائر الذات الإلهية', en: 'Divine Pronouns' },
        { icon: '⚖️', ar: 'التوازن في الأزواج', en: 'Antonym Pairs' },
        { icon: '📅', ar: 'الكلمات التقويمية', en: 'Calendar Claims' },
        { icon: '🔢', ar: 'حساب الجُمَّل', en: 'Abjad Numerals' },
        { icon: '🔬', ar: 'الإشارات العلمية', en: 'Scientific References' },
        { icon: '💡', ar: 'استنتاجات البيانات', en: 'Data-Driven Insights' },
      ],
      insights: [
        { icon: '📊', cat_ar: 'تكرار الكلمات', cat_en: 'Word Frequency',
          ar: 'الكلمة الأكثر تكراراً هي "' + DATA.topWords[0].w + '" — تظهر ' + DATA.topWords[0].c.toLocaleString() + ' مرة. هذا يعني أنها تظهر كل 4 آيات تقريباً.',
          en: 'The most frequent word is "' + DATA.topWords[0].w + '" — appearing ' + DATA.topWords[0].c.toLocaleString() + ' times. That means it appears roughly every 4 verses.' },
        { icon: '📏', cat_ar: 'بنية الآيات', cat_en: 'Verse Structure',
          ar: 'الآيات المدنية أطول بمعدل ' + (DATA.medinanAvgWc / DATA.meccanAvgWc).toFixed(1) + 'x من المكية — يعكس التحول من الإيمان إلى التشريع.',
          en: 'Medinan verses are ' + (DATA.medinanAvgWc / DATA.meccanAvgWc).toFixed(1) + 'x longer — reflecting the shift from faith to legislation.' },
        { icon: '📚', cat_ar: 'ثراء المفردات', cat_en: 'Vocabulary Richness',
          ar: 'القرآن يحتوي على ' + DATA.uniqueWords.toLocaleString() + ' كلمة فريدة. منها ' + DATA.hapax.toLocaleString() + ' (' + (DATA.hapax/DATA.uniqueWords*100).toFixed(0) + '%) تظهر مرة واحدة فقط (هاباكس ليغومينا).',
          en: DATA.uniqueWords.toLocaleString() + ' unique words. Of these, ' + DATA.hapax.toLocaleString() + ' (' + (DATA.hapax/DATA.uniqueWords*100).toFixed(0) + '%) appear only once (hapax legomena).' },
        { icon: '💬', cat_ar: 'النبرة العاطفية', cat_en: 'Emotional Tone',
          ar: 'لغة الرحمة والهداية تشكلان الأغلبية — النبرة الغالبة هي الرحمة وليس التخويف.',
          en: 'Mercy and guidance language dominates — the prevailing tone is compassion, not fear.' },
        { icon: '🌐', cat_ar: 'كثافة اللغة', cat_en: 'Language Density',
          ar: 'العربية لغة كثيفة صرفياً — كلمة عربية واحدة تحتاج 1.7 كلمة إنجليزية في المتوسط للترجمة.',
          en: 'Arabic is morphologically dense — one Arabic word needs 1.7 English words on average to translate.' },
        { icon: '🔁', cat_ar: 'أنماط التكرار', cat_en: 'Repetition Patterns',
          ar: 'التكرار في القرآن ليس عشوائياً بل يخدم التأكيد والإيقاع — كل تكرار له وظيفة بلاغية.',
          en: 'Repetition is not random but serves emphasis and rhythm — every repetition has a rhetorical function.' },
        { icon: '✨', cat_ar: 'الصفات الإلهية', cat_en: 'Divine Attributes',
          ar: 'تركيز النص على صفات الرحمة والحكمة يفوق صفات القوة والعظمة — النص يركز على القرب لا البعد.',
          en: 'The text emphasizes mercy and wisdom attributes over power and might — focusing on closeness, not distance.' },
        { icon: '⏳', cat_ar: 'الآخرة والدنيا', cat_en: 'Afterlife vs Worldly',
          ar: 'مفردات الآخرة تفوق مفردات الدنيا — النص يضع الحياة في إطار أخروي.',
          en: 'Afterlife vocabulary outweighs worldly — the text frames life through an eschatological lens.' },
      ]
    };
  },
  computed: {
    overviewKPIs() {
      return [
        { ar: 'سور', en: 'Surahs', val: '114' },
        { ar: 'آيات', en: 'Verses', val: this.D.totalVerses.toLocaleString() },
        { ar: 'كلمات', en: 'Words', val: this.D.totalWords.toLocaleString() },
        { ar: 'كلمات فريدة', en: 'Unique', val: this.D.uniqueWords.toLocaleString() },
        { ar: 'مكية', en: 'Meccan', val: String(this.D.meccanSurahs) },
        { ar: 'مدنية', en: 'Medinan', val: String(this.D.medinanSurahs) },
      ];
    },
    filteredSciRefs() {
      if (this.sciFilter === 'all') return this.D.scientificRefs;
      return this.D.scientificRefs.filter(r => r.cat_en === this.sciFilter);
    }
  },
  methods: {
    L(ar, en) { return this.lang === 'ar' ? ar : en; },
    totalSentiment(key) { return this.D.sentiment.reduce((sum, s) => sum + s[key], 0); },
    goTo(idx) {
      this.currentPage = idx;
      window.scrollTo({ top: 0, behavior: 'smooth' });
      this.$nextTick(() => { this.renderCharts(); this.animatePage(); });
    },
    calcAbjad() {
      const ABJAD_MAP = {};
      this.D.abjadTable.forEach(a => ABJAD_MAP[a.l] = a.v);
      const text = this.abjadInput.replace(/[\u0610-\u061A\u064B-\u065F\u0670]/g, '')
        .replace(/[ٱإأآا]/g, 'ا').replace(/[ؤئ]/g, 'ء').replace(/ة/g, 'ه').replace(/ى/g, 'ي');
      const letters = [];
      let total = 0;
      for (const ch of text) {
        const v = ABJAD_MAP[ch] || 0;
        if (v > 0) { letters.push({ l: ch, v }); total += v; }
      }
      this.abjadLetters = letters;
      this.abjadTotal = total;
    },
    animatePage() {
      if (typeof gsap === 'undefined') return;
      // Hero animations
      gsap.fromTo('[data-anim="hero"]', { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.8, stagger: 0.15, ease: 'power3.out' });
      // Section headers
      gsap.fromTo('[data-anim="section"]', { opacity: 0, x: 30 },
        { opacity: 1, x: 0, duration: 0.6, stagger: 0.1, ease: 'power2.out', delay: 0.3 });
      // KPI flying cards
      gsap.fromTo('.kpi', { opacity: 0, y: 50, rotateX: 15 },
        { opacity: 1, y: 0, rotateX: 0, duration: 0.7, stagger: 0.1, ease: 'back.out(1.2)', delay: 0.2 });
      // Charts
      gsap.fromTo('[data-anim="chart"]', { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.8, stagger: 0.15, ease: 'power2.out', delay: 0.4 });
      // Insight boxes
      gsap.fromTo('[data-anim="insight"]', { opacity: 0, x: 25 },
        { opacity: 1, x: 0, duration: 0.7, stagger: 0.1, ease: 'power2.out', delay: 0.5 });
      // Cards
      gsap.fromTo('[data-anim="card"]', { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: 'power2.out', delay: 0.3 });
      // Waw cards
      gsap.fromTo('[data-anim="waw"]', { opacity: 0, scale: 0.85 },
        { opacity: 1, scale: 1, duration: 0.8, stagger: 0.2, ease: 'back.out(1.5)', delay: 0.4 });
    },
    renderCharts() {
      const D = this.D;
      const isAr = this.lang === 'ar';
      const plotCfg = { responsive: true, displayModeBar: false };
      const baseLay = { plot_bgcolor: 'rgba(0,0,0,0)', paper_bgcolor: 'rgba(0,0,0,0)' };

      if (this.currentPage === 0) {
        const el = document.getElementById('chart-surah-bars');
        if (el) {
          const mecca = D.surahStats.filter(s => s.p === 'Mecca');
          const medina = D.surahStats.filter(s => s.p === 'Medina');
          Plotly.newPlot(el, [
            { x: mecca.map(s => s.n), y: mecca.map(s => s.vc), type: 'bar', name: isAr ? 'مكة' : 'Mecca', marker: { color: '#B7094C' } },
            { x: medina.map(s => s.n), y: medina.map(s => s.vc), type: 'bar', name: isAr ? 'المدينة' : 'Medina', marker: { color: '#0091AD' } }
          ], { ...baseLay, height: 350, xaxis: { title: isAr ? 'رقم السورة' : 'Surah #' },
            yaxis: { title: isAr ? 'عدد الآيات' : 'Verse Count' }, legend: { orientation: 'h', y: 1.1 }, margin: { t: 30 }
          }, plotCfg);
        }
      }

      if (this.currentPage === 1) {
        const el = document.getElementById('chart-word-freq');
        if (el) {
          const words = D.topWords.slice().reverse();
          Plotly.newPlot(el, [{
            y: words.map(w => w.w), x: words.map(w => w.c), type: 'bar', orientation: 'h',
            text: words.map(w => w.c.toLocaleString()), textposition: 'outside',
            marker: { color: words.map((_, i) => `rgba(27,67,50,${0.3 + 0.7 * i / words.length})`) }
          }], { ...baseLay, height: Math.max(550, words.length * 24),
            yaxis: { tickfont: { size: 16, family: 'Amiri' }, side: 'right', title: '' },
            xaxis: { title: isAr ? 'التكرار' : 'Frequency', side: 'top' }, margin: { r: 120, t: 30, b: 10 }
          }, plotCfg);
        }
      }

      if (this.currentPage === 2) {
        const el = document.getElementById('chart-sentiment');
        if (el) {
          Plotly.newPlot(el, [
            { x: D.sentiment.map(s => s.n), y: D.sentiment.map(s => s.mercy), type: 'bar', name: isAr ? 'رحمة' : 'Mercy', marker: { color: '#52B788' } },
            { x: D.sentiment.map(s => s.n), y: D.sentiment.map(s => s.warning), type: 'bar', name: isAr ? 'تحذير' : 'Warning', marker: { color: '#B7094C' } },
            { x: D.sentiment.map(s => s.n), y: D.sentiment.map(s => s.guidance), type: 'bar', name: isAr ? 'هداية' : 'Guidance', marker: { color: '#D4A574' } },
            { x: D.sentiment.map(s => s.n), y: D.sentiment.map(s => s.hope), type: 'bar', name: isAr ? 'أمل' : 'Hope', marker: { color: '#0091AD' } }
          ], { ...baseLay, barmode: 'stack', height: 400, xaxis: { title: isAr ? 'رقم السورة' : 'Surah #' },
            yaxis: { title: isAr ? 'عدد الكلمات' : 'Word Count' }, legend: { orientation: 'h', y: 1.1 }, margin: { t: 30 }
          }, plotCfg);
        }
      }

      if (this.currentPage === 3) {
        const el = document.getElementById('chart-sentiment-pie');
        if (el) {
          const m = this.totalSentiment('mercy'), w = this.totalSentiment('warning'),
                g = this.totalSentiment('guidance'), h = this.totalSentiment('hope');
          Plotly.newPlot(el, [{
            values: [m, w, g, h],
            labels: isAr ? ['رحمة','تحذير','هداية','أمل'] : ['Mercy','Warning','Guidance','Hope'],
            type: 'pie', hole: 0.45, textinfo: 'percent+label',
            marker: { colors: ['#52B788','#B7094C','#D4A574','#0091AD'] },
            textfont: { family: 'Amiri', size: 14 }
          }], { ...baseLay, height: 400, showlegend: false, margin: { t: 20 } }, plotCfg);
        }
      }

      if (this.currentPage === 5) {
        const el = document.getElementById('chart-letters');
        if (el) {
          Plotly.newPlot(el, [{
            x: D.letters.map(l => l.l), y: D.letters.map(l => l.c), type: 'bar',
            text: D.letters.map(l => l.c.toLocaleString()), textposition: 'outside',
            marker: { color: D.letters.map((_, i) => `rgba(27,67,50,${0.3 + 0.7 * (1 - i / D.letters.length)})`) }
          }], { ...baseLay, height: 420, xaxis: { tickfont: { size: 22, family: 'Amiri' }, title: '' },
            yaxis: { title: isAr ? 'التكرار' : 'Frequency' }, margin: { t: 20 }
          }, plotCfg);
        }
      }

      if (this.currentPage === 6) {
        const el = document.getElementById('chart-pronouns');
        if (el) {
          const p = D.pronouns;
          Plotly.newPlot(el, [{
            values: [p.we, p.i, p.he],
            labels: isAr ? ['نحن (تعظيم)','أنا (مفرد)','هو (غائب)'] : ['We (Majestic)','I (Singular)','He (3rd Person)'],
            type: 'pie', hole: 0.45, textinfo: 'percent+label',
            marker: { colors: ['#2D6A4F','#D4A574','#0091AD'] },
            textfont: { family: 'Amiri', size: 14 }
          }], { ...baseLay, height: 400, showlegend: false, margin: { t: 20 } }, plotCfg);
        }
      }

      if (this.currentPage === 10) {
        const el = document.getElementById('chart-sci-cats');
        if (el) {
          const cats = D.sciCategories;
          const labels = cats.map(c => {
            if (isAr) {
              const ref = D.scientificRefs.find(r => r.cat_en === c.cat);
              return ref ? ref.cat_ar : c.cat;
            }
            return c.cat;
          });
          Plotly.newPlot(el, [{
            y: labels.reverse(), x: cats.map(c => c.count).reverse(),
            type: 'bar', orientation: 'h',
            text: cats.map(c => c.count).reverse(), textposition: 'outside',
            marker: { color: cats.map((_, i) => `rgba(27,67,50,${0.4 + 0.6 * i / cats.length})`).reverse() }
          }], { ...baseLay, height: Math.max(350, cats.length * 35),
            yaxis: { tickfont: { size: 13, family: 'Inter' }, side: 'right', title: '' },
            xaxis: { title: isAr ? 'عدد الإشارات' : 'Reference Count' }, margin: { r: 160, t: 20, b: 30 }
          }, plotCfg);
        }
      }
    }
  },
  watch: {
    currentPage() { this.$nextTick(() => { this.renderCharts(); this.animatePage(); }); },
    lang() { this.$nextTick(() => this.renderCharts()); },
    sciFilter() { this.$nextTick(() => this.animatePage()); }
  },
  mounted() {
    this.renderCharts();
    this.animatePage();
    // Particle background
    this.initParticles();
  },
  created() {
    this.initParticles = () => {
      const canvas = document.getElementById('particles');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      const particles = [];
      for (let i = 0; i < 40; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          r: Math.random() * 2 + 0.5,
          dx: (Math.random() - 0.5) * 0.3,
          dy: (Math.random() - 0.5) * 0.3,
          a: Math.random() * 0.15 + 0.05
        });
      }
      function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(82, 183, 136, ${p.a})`;
          ctx.fill();
          p.x += p.dx; p.y += p.dy;
          if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
          if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
        });
        requestAnimationFrame(draw);
      }
      draw();
      window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });
    };
  }
}).mount('#app');
</script>
</body>
</html>'''

out_path = os.path.join(BASE, "QuranAnalytics.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"Built cinematic HTML app: {out_path}")
print(f"File size: {os.path.getsize(out_path)} bytes ({os.path.getsize(out_path)//1024}KB)")
