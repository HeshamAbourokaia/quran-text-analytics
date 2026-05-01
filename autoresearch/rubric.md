# Vision-judge rubric for chart-radar

You are judging a single Plotly radar chart that visualises "Surah DNA" — a 12-axis fingerprint of selected Quran chapters against a Quran-average baseline (the dotted ghost trace).

The chart is part of an Electron app for Quran text analytics. The audience is bilingual Arabic/English readers exploring patterns across chapters. The data is sacred subject matter, so cultural fit matters.

Score each of the 7 criteria from 1 (very poor) to 10 (excellent). Then give an `overall` score 1-10 — your independent gestalt judgement of the chart's quality, NOT a mean. End with `notes` ≤ 40 words explaining the *single* most useful observation.

Return STRICT JSON, no preamble, no trailing prose:

```json
{
  "scores": {
    "readability": <1-10>,
    "visual_hierarchy": <1-10>,
    "color_harmony": <1-10>,
    "info_density": <1-10>,
    "spatial_balance": <1-10>,
    "aesthetic_polish": <1-10>,
    "cultural_fit": <1-10>
  },
  "overall": <1-10>,
  "notes": "<= 40 words"
}
```

## Criteria definitions

1. **Readability** — Are all 12 axis labels actually readable at this font size and rotation? Are radial tick values legible? Hover tooltips aren't shown, but the static labels must work.

2. **Visual hierarchy** — Does the eye know what's primary (selected surah polygons) versus secondary (the ghost-dotted Quran average baseline)? Or do they fight each other?

3. **Color harmony** — Is the palette pleasant, distinguishable across all 5 trace slots, not garish? Are filled regions translucent enough to overlap without losing identity? Any colors that clash with the cream/Amiri Arabic typography?

4. **Information density** — Enough visual material to feel substantive, but without crowding. A radar chart with 12 axes naturally pushes density limits. Score how well this balance is held.

5. **Spatial balance** — Margins reasonable. Legend placed where it doesn't crowd or get lost. Polar plot well-centered. Empty quadrants of the page not awkward.

6. **Aesthetic polish** — Overall feeling that this looks designed and intentional, not thrown together. Premium-product feel, or amateur output?

7. **Cultural fit** (weighted 1.5× in combined score) — Arabic typography rendered legibly. Respect for the Quran subject matter — the chart should not feel garish, irreverent, or "data-bro" given what it represents.

## Tie-breaking guidance

- A chart that's "fine" but unremarkable is overall ~6.
- A chart that's clean and useful is overall ~7.
- A chart that's notably designed is overall ~8.
- A chart that's exceptional is overall ~9. Reserve 10 for charts where you have nothing to suggest.
- Charts with rendering errors, label collisions, or unreadable text are overall ≤ 4 regardless of other scores.
