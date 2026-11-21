package com.hesham.quraninsights;

import android.net.Uri;

import com.google.androidbrowserhelper.trusted.LauncherActivity;

/** Opens the site full screen in Chrome. A phone set to Arabic opens the Arabic site, unless a link already chose. */
public class Launcher extends LauncherActivity {
    @Override
    protected Uri getLaunchingUrl() {
        Uri url = super.getLaunchingUrl();
        if (Verses.arabic() && url.getQueryParameter("lang") == null && "quraninsights.vercel.app".equals(url.getHost())) {
            url = url.buildUpon().appendQueryParameter("lang", "ar").build();
        }
        return url;
    }
}
