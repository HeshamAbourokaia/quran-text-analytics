package com.hesham.quraninsights;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.widget.RemoteViews;

import java.util.Calendar;

/**
 * The home-screen widget: a verse of the day in the mushaf's Arabic with Pickthall's English. A tap on the verse opens
 * it in the Reader; "Another verse" moves on. It changes by itself at local midnight, without waking the phone.
 */
public class VerseWidget extends AppWidgetProvider {
    static final String NEXT = "com.hesham.quraninsights.NEXT";
    static final String MIDNIGHT = "com.hesham.quraninsights.MIDNIGHT";
    private static final String PREFS = "widget", STEP = "step";

    @Override
    public void onUpdate(Context c, AppWidgetManager m, int[] ids) {
        for (int id : ids) m.updateAppWidget(id, views(c, id));
        atMidnight(c);
    }

    @Override
    public void onReceive(Context c, Intent i) {
        String a = i.getAction();
        if (NEXT.equals(a)) {
            SharedPreferences p = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
            p.edit().putInt(STEP, p.getInt(STEP, 0) + 1).apply();
            refreshAll(c);
        } else if (MIDNIGHT.equals(a) || Intent.ACTION_TIME_CHANGED.equals(a)
                || Intent.ACTION_TIMEZONE_CHANGED.equals(a) || Intent.ACTION_LOCALE_CHANGED.equals(a)) {
            refreshAll(c);
        } else {
            super.onReceive(c, i);
        }
    }

    static void refreshAll(Context c) {
        AppWidgetManager m = AppWidgetManager.getInstance(c);
        int[] ids = m.getAppWidgetIds(new ComponentName(c, VerseWidget.class));
        for (int id : ids) m.updateAppWidget(id, views(c, id));
        atMidnight(c);
    }

    static RemoteViews views(Context c, int id) {
        boolean ar = Verses.arabic();
        int step = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getInt(STEP, 0);
        Verses.Verse v = Verses.pick(c, step);
        RemoteViews r = new RemoteViews(c.getPackageName(), R.layout.widget_verse);
        if (v == null) return r;
        // the labels in the same language as the verse's reference, whatever language the home screen draws in
        Context lc = inLanguage(c, ar);
        r.setTextViewText(R.id.kicker, lc.getString(R.string.kicker));
        r.setTextViewText(R.id.read, lc.getString(R.string.read));
        r.setTextViewText(R.id.next, lc.getString(R.string.next));
        r.setTextViewText(R.id.ref, v.reference(ar));
        r.setTextViewText(R.id.arabic, v.arabic);
        r.setTextViewText(R.id.english, v.english);

        // the whole verse opens it in the Reader, in the app
        Intent open = new Intent(Intent.ACTION_VIEW, v.link(ar)).setClass(c, Launcher.class)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent openPi = PendingIntent.getActivity(c, id, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        r.setOnClickPendingIntent(R.id.body, openPi);
        r.setOnClickPendingIntent(R.id.read, openPi);

        Intent next = new Intent(c, VerseWidget.class).setAction(NEXT);
        r.setOnClickPendingIntent(R.id.next, PendingIntent.getBroadcast(c, 0, next, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE));
        return r;
    }

    static Context inLanguage(Context c, boolean ar) {
        android.content.res.Configuration conf = new android.content.res.Configuration(c.getResources().getConfiguration());
        conf.setLocale(ar ? java.util.Locale.forLanguageTag("ar") : java.util.Locale.ENGLISH);
        return c.createConfigurationContext(conf);
    }

    /** a new verse at the next local midnight; an inexact, non-waking alarm, so it waits for the phone to wake */
    static void atMidnight(Context c) {
        AlarmManager am = c.getSystemService(AlarmManager.class);
        if (am == null) return;
        Calendar t = Calendar.getInstance();
        t.add(Calendar.DAY_OF_YEAR, 1);
        t.set(Calendar.HOUR_OF_DAY, 0); t.set(Calendar.MINUTE, 0); t.set(Calendar.SECOND, 5); t.set(Calendar.MILLISECOND, 0);
        Intent i = new Intent(c, VerseWidget.class).setAction(MIDNIGHT);
        PendingIntent pi = PendingIntent.getBroadcast(c, 1, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        am.set(AlarmManager.RTC, t.getTimeInMillis(), pi);
    }
}
