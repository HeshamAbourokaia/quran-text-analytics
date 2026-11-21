package com.hesham.quraninsights;

import android.content.Context;
import android.net.Uri;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Calendar;
import java.util.Locale;

/** The widget's verses (assets/verses.json, written by tools/make_verses.js) and which one a day shows. */
final class Verses {
    static final class Verse {
        final int surah, from, to;
        final String arabic, english, nameEn, nameAr;
        Verse(JSONObject o) {
            surah = o.optInt("s"); from = o.optInt("a"); to = o.optInt("b");
            arabic = o.optString("ar"); english = o.optString("en"); nameEn = o.optString("nameEn"); nameAr = o.optString("nameAr");
        }
        /** "Al-A'raf 7:23", or in Arabic "الأعراف ٧:٢٣" */
        String reference(boolean ar) {
            String n = surah + ":" + from + (to > from ? "-" + to : "");
            return ar ? nameAr + " " + arabicDigits(n) : nameEn + " " + n;
        }
        /** the verse in the site's Reader, in the phone's language */
        Uri link(boolean ar) {
            Uri.Builder b = Uri.parse("https://quraninsights.vercel.app/reader").buildUpon()
                .appendQueryParameter("s", String.valueOf(surah)).appendQueryParameter("v", String.valueOf(from));
            if (ar) b.appendQueryParameter("lang", "ar");
            return b.build();
        }
    }

    private static JSONArray all;

    static synchronized JSONArray load(Context c) {
        if (all != null) return all;
        try (InputStream in = c.getAssets().open("verses.json")) {
            all = new JSONArray(new String(in.readAllBytes(), StandardCharsets.UTF_8));
        } catch (Exception e) {
            all = new JSONArray();
        }
        return all;
    }

    /** The same verse all day, a new one each day; "Another verse" moves on by `step`. */
    static Verse pick(Context c, int step) {
        JSONArray list = load(c);
        if (list.length() == 0) return null;
        int i = Math.floorMod(dayNumber() + step, list.length());
        return new Verse(list.optJSONObject(i));
    }

    /** days since 1 Jan 1970 in the phone's own time zone, so the verse changes at local midnight */
    static int dayNumber() {
        Calendar now = Calendar.getInstance();
        long local = now.getTimeInMillis() + now.get(Calendar.ZONE_OFFSET) + now.get(Calendar.DST_OFFSET);
        return (int) Math.floorDiv(local, 86_400_000L);
    }

    static boolean arabic() { return "ar".equals(Locale.getDefault().getLanguage()); }

    static String arabicDigits(String s) {
        StringBuilder b = new StringBuilder(s.length());
        for (char ch : s.toCharArray()) b.append(ch >= '0' && ch <= '9' ? (char) ('٠' + (ch - '0')) : ch);
        return b.toString();
    }

    private Verses() {}
}
